from http.client import HTTPConnection
import json
from threading import Thread

import pytest

from rulespec_extrapolator.review import create_server
from rulespec_extrapolator.review_store import ReviewError
from test_review_store import action, make_run


@pytest.fixture
def server(tmp_path):
    run_dir = make_run(tmp_path, extra_source='</pre><script>window.sourceExecuted=true</script><img src=x onerror="alert(1)">',
                       extraction_refusals=[{"window_id": "bad-window", "attempt_id": "attempt-0001", "code": "malformed_json"}])
    instance = create_server(run_dir, port=0)
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield instance
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=5)


def request(server, method, path, body=None, headers=None):
    client = HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
    try:
        client.request(method, path, body=body, headers=headers or {})
        response = client.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        client.close()


def write_headers(server, **changes):
    return {"Content-Type": "application/json", "Origin": server.url,
            "X-CSRF-Token": server.csrf_token, **changes}


def test_http_action_and_reopen_use_the_same_store(server):
    status, _, payload = request(server, "GET", "/api/session")
    assert status == 200
    assert json.loads(payload)["csrf_token"] == server.csrf_token
    _, _, payload = request(server, "GET", "/api/snapshot")
    snapshot = json.loads(payload)
    body = json.dumps(action(snapshot, "approve", [snapshot["accepted"][0]["id"]]))
    status, headers, payload = request(server, "POST", "/api/actions", body, write_headers(server))
    assert status == 200
    result = json.loads(payload)
    assert result["revision"] == 1
    assert result["attestations"][0]["attestor_kind"] == "rkaf:aiAgent"
    assert headers["Cache-Control"] == "no-store"
    status, _, payload = request(server, "POST", "/api/actions", body, write_headers(server))
    assert status == 409
    assert json.loads(payload)["revision"] == 1
    assert server.store.snapshot()["revision"] == 1


def test_audit_gaps_are_visible_and_become_stale_after_a_correction(monkeypatch, tmp_path):
    from rulespec_extrapolator import audit, extraction
    from test_audit import draft, answers, provider
    book = draft()
    run_dir = tmp_path / "draft"
    run_dir.mkdir()
    for filename, value in (("rulebook.json", book), ("run.json", book["run"]), ("document.json", book["document"])):
        extraction._save(run_dir / filename, value)
    env, _ = provider(monkeypatch, tmp_path, answers())
    audit.audit_run(book, tmp_path / "audit", env_file=env)
    instance = create_server(run_dir, port=0, audit_dir=tmp_path / "audit")
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        _, _, payload = request(instance, "GET", "/api/snapshot")
        before = json.loads(payload)
        assert before["source_audit"]["current"] is True
        assert before["source_audit"]["report"]["coverage"]["missing"] == 1
        body = action(before, "edit", [before["accepted"][0]["id"]], replacements=[{
            "summary": "Visitors must present one or more of a receipt or an invoice.",
            "alternative_quotes": ["a receipt", "an invoice"],
        }])
        status, _, payload = request(instance, "POST", "/api/actions", json.dumps(body), write_headers(instance))
        assert status == 200
        assert json.loads(payload)["source_audit"]["current"] is False
        _, _, payload = request(instance, "GET", "/api/snapshot")
        assert json.loads(payload)["source_audit"]["current"] is False
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=5)


def test_foreign_hosts_origins_and_missing_csrf_cannot_write(server):
    snapshot = server.store.snapshot()
    body = json.dumps(action(snapshot, "reject", [snapshot["accepted"][0]["id"]]))
    cases = [
        write_headers(server, Host="attacker.example:1234"),
        write_headers(server, Origin="https://attacker.example"),
        write_headers(server, Origin="null"),
        {"Content-Type": "application/json", "X-CSRF-Token": server.csrf_token},
        {"Content-Type": "application/json", "Origin": server.url},
        write_headers(server, **{"X-CSRF-Token": "wrong"}),
        write_headers(server, **{"X-CSRF-Token": "é"}),
        write_headers(server, **{"Sec-Fetch-Site": "cross-site"}),
    ]
    for headers in cases:
        status, _, _ = request(server, "POST", "/api/actions", body, headers)
        assert status == 403
    assert request(server, "GET", "/api/session", headers={"Host": "rebind.example"})[0] == 403
    assert server.store.snapshot()["revision"] == 0


def test_only_known_assets_are_served_and_text_cannot_become_markup(server):
    status, headers, html = request(server, "GET", "/")
    assert status == 200
    assert b"sourceExecuted" not in html
    assert b"Choose reviewer type" in html
    assert b">Add rule</button>" in html
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert "script-src 'self'" in headers["Content-Security-Policy"]
    for path in ("/document.json", "/run.json", "/review.sqlite3", "/../../run.json", "/static/../review_store.py", "/static/%2e%2e/review_store.py"):
        assert request(server, "GET", path)[0] == 404
    status, _, script = request(server, "GET", "/static/review.js")
    assert status == 200
    assert b"innerHTML" not in script
    assert b"insertAdjacentHTML" not in script
    assert b"textContent" in script and b"createTextNode" in script
    status, headers, payload = request(server, "GET", "/api/snapshot")
    assert status == 200
    assert headers["Content-Type"].startswith("application/json")
    assert "<script>window.sourceExecuted=true</script>" in json.loads(payload)["document"]["text"]
    assert json.loads(payload)["extraction_refusals"] == [
        {"window_id": "bad-window", "attempt_id": "attempt-0001", "code": "malformed_json"},
    ]


def test_http_add_requires_no_existing_target_and_records_agent_origin(server):
    snapshot = server.store.snapshot()
    request_body = action(snapshot, "add", [], replacements=[{
        "kind": "requirement", "summary": "Supervisors must retain records.", "actor": "Supervisors",
        "actor_quote": "Supervisors", "quote": "retain records", "action": "retain", "action_quote": "retain",
    }])
    status, _, payload = request(server, "POST", "/api/actions", json.dumps(request_body), write_headers(server))
    assert status == 200
    result = json.loads(payload)
    event = result["history"][-1]
    assert event["action"] == "add"
    assert event["targets"] == []
    assert event["replacements"][0]["origin"] == "aiSuggested"
    assert "supersedes" not in event["replacements"][0]


def test_malformed_requests_fail_without_a_review_event(server):
    assert request(server, "POST", "/api/actions", "{}", write_headers(server, **{"Content-Type": "text/plain"}))[0] == 415
    assert request(server, "POST", "/api/actions", "broken", write_headers(server))[0] == 400
    assert request(server, "POST", "/api/actions", '{"expected_revision":NaN}', write_headers(server))[0] == 400
    assert request(server, "POST", "/api/actions", "{}", write_headers(server))[0] == 422
    assert request(server, "POST", "/api/actions", "x", write_headers(server, **{"Content-Length": "1000001"}))[0] == 413
    assert server.store.snapshot()["revision"] == 0


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.2", "example.test"])
def test_server_refuses_non_loopback_listeners(tmp_path, host):
    with pytest.raises(ReviewError, match="loopback"):
        create_server(tmp_path / "missing-run", host=host, port=0)
