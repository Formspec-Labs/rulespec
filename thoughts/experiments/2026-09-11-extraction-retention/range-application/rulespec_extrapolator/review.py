"""A loopback-only HTTP interface for the local review workflow."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import ipaddress
import json
from pathlib import Path
import secrets
import socket
from urllib.parse import urlsplit

from .review_store import ReviewError, ReviewStore, RevisionConflict


_ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/static/review.js": ("review.js", "text/javascript; charset=utf-8"),
    "/static/review.css": ("review.css", "text/css; charset=utf-8"),
}
_MAX_BODY = 1_000_000


class ReviewHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, host: str, port: int, store: ReviewStore, audit_dir=None) -> None:
        if ":" in host:
            self.address_family = socket.AF_INET6
        self.store = store
        self.audit = None
        if audit_dir is not None:
            from .audit import load_audit
            self.audit = load_audit(audit_dir)
            if self.audit["book"]["document"] != store.document:
                raise ReviewError("The audit describes a different source document.")
        self.csrf_token = secrets.token_urlsafe(32)
        super().__init__((host, port), ReviewHandler)
        bound_port = self.server_address[1]
        address = f"[{host}]" if ":" in host else host
        self.allowed_hosts = {f"{address}:{bound_port}", f"localhost:{bound_port}"}
        if bound_port == 80:
            self.allowed_hosts.update({address, "localhost"})
        self.url = f"http://{address}:{bound_port}"

    def decorate(self, snapshot):
        if self.audit is not None:
            from .evaluation import content_digest
            expected = self.audit["run"]["rulebook_sha256"]
            current = content_digest(snapshot) == expected or (snapshot["revision"] == 0 and content_digest(self.store.base) == expected)
            snapshot["source_audit"] = {"current": current, "report": self.audit["report"],
                                       "units": self.audit["labels"]["expected_units"], "accounting": self.audit["accounting"]}
        return snapshot


class ReviewHandler(BaseHTTPRequestHandler):
    server: ReviewHTTPServer
    server_version = "RulespecReview"
    sys_version = ""

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, format: str, *args: object) -> None:
        # Source text, reviewer names, and request data stay out of HTTP logs.
        pass

    def _reply(self, status: int, body: bytes, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, value: object) -> None:
        self._reply(status, json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8"))

    def _trusted_request(self, *, write: bool = False) -> bool:
        hosts = self.headers.get_all("Host", [])
        if len(hosts) != 1 or hosts[0].lower() not in self.server.allowed_hosts:
            self._json(403, {"error": "Use the local review address to open this run."})
            return False
        origins = self.headers.get_all("Origin", [])
        if (write or origins) and (len(origins) != 1 or origins[0] != "http://" + hosts[0].lower()):
            self._json(403, {"error": "Review changes must come from this local review page."})
            return False
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            self._json(403, {"error": "Cross-site review requests are not allowed."})
            return False
        if write:
            tokens = self.headers.get_all("X-CSRF-Token", [])
            if len(tokens) != 1 or not secrets.compare_digest(tokens[0].encode("utf-8"), self.server.csrf_token.encode("utf-8")):
                self._json(403, {"error": "The review session is missing or expired. Reload this page."})
                return False
        return True

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        if not self._trusted_request():
            return
        path = urlsplit(self.path).path
        if path in _ASSETS:
            name, content_type = _ASSETS[path]
            content = files("rulespec_extrapolator").joinpath("static", name).read_bytes()
            self._reply(200, content, content_type)
        elif path == "/api/session":
            self._json(200, {"csrf_token": self.server.csrf_token})
        elif path == "/api/snapshot":
            try:
                self._json(200, self.server.decorate(self.server.store.snapshot()))
            except ReviewError as exc:
                self._json(409, {"error": str(exc)})
        else:
            self._json(404, {"error": "This review page does not exist."})

    def do_POST(self) -> None:
        if not self._trusted_request(write=True):
            return
        if urlsplit(self.path).path != "/api/actions":
            self._json(404, {"error": "This review action endpoint does not exist."})
            return
        if self.headers.get_content_type() != "application/json" or self.headers.get("Transfer-Encoding"):
            self._json(415, {"error": "Send review actions as JSON."})
            return
        lengths = self.headers.get_all("Content-Length", [])
        try:
            length = int(lengths[0]) if len(lengths) == 1 else -1
        except ValueError:
            length = -1
        if not 0 < length <= _MAX_BODY:
            self._json(413, {"error": "The review request is empty or too large."})
            return
        try:
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError("Incomplete request")
            request = json.loads(body, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Non-finite JSON")))
        except (ValueError, UnicodeError, TimeoutError):
            self._json(400, {"error": "The review request is not valid JSON."})
            return
        try:
            self._json(200, self.server.decorate(self.server.store.apply(request)))
        except RevisionConflict as exc:
            self._json(409, {"error": str(exc), "revision": exc.current})
        except ReviewError as exc:
            self._json(422, {"error": str(exc)})


def create_server(run_dir: str | Path, host: str = "127.0.0.1", port: int = 8765, *, audit_dir=None) -> ReviewHTTPServer:
    """Create a server bound to a numeric loopback address (or localhost)."""
    if host == "localhost":
        host = "127.0.0.1"
    try:
        if not ipaddress.ip_address(host).is_loopback:
            raise ValueError
    except ValueError as exc:
        raise ReviewError("Local review can only listen on a loopback address.") from exc
    return ReviewHTTPServer(host, port, ReviewStore(run_dir), audit_dir=audit_dir)


def serve(run_dir: str | Path, host: str = "127.0.0.1", port: int = 8765, *, audit_dir=None) -> None:
    """Serve the run until interrupted."""
    server = create_server(run_dir, host=host, port=port, audit_dir=audit_dir)
    print(f"Review this run at {server.url}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
