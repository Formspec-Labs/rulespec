"""Bounded local blob publication, independent of source and dataset lifecycles."""

from __future__ import annotations

import hashlib
import os
import secrets
import stat
from collections.abc import Iterable, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path

from ._artifact import (
    DEFAULT_READ_CHUNK_BYTES,
    ArtifactVerificationError,
    LocalFileState,
    MemberSourceError,
    PinnedLocalDirectory,
    _digest,
    validate_object_key,
)


class BlobIntegrityError(ValueError):
    """Blob bytes or the destination differ from their immutable identity."""


class BlobLimitError(ValueError):
    """A declared or observed blob exceeds the caller's byte limit."""


@dataclass(frozen=True, slots=True)
class LocalBlobWrite:
    """Effect of a put; bytes_written counts staging even when another writer wins."""

    digest: str
    object_key: str
    byte_size: int
    reused: bool
    bytes_written: int


def _nonnegative(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")


def _identity(descriptor: int) -> tuple[int, int]:
    state = os.fstat(descriptor)
    return state.st_dev, state.st_ino


def _child(parent: int, name: str, *, create: bool) -> int:
    if create:
        try:
            os.mkdir(name, dir_fd=parent)
        except FileExistsError:
            pass
        else:
            os.fsync(parent)
    try:
        return PinnedLocalDirectory._open_relative(parent, name, directory=True, path=name)
    except (ArtifactVerificationError, MemberSourceError) as error:
        raise ValueError("blob store layout is missing or is not a present non-symlink directory") from error


def _exists(directory: int, name: str) -> bool:
    try:
        state = os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if not stat.S_ISREG(state.st_mode):
        raise BlobIntegrityError("blob destination is not a regular file")
    return True


def _verify(directory: int, name: str, digest: str, byte_size: int) -> None:
    try:
        # O_NONBLOCK prevents a raced-in FIFO from blocking before fstat.
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    except OSError as error:
        raise BlobIntegrityError(f"cannot open immutable blob: {digest}") from error
    try:
        before = LocalFileState.from_stat(os.fstat(descriptor))
        if not stat.S_ISREG(before.mode) or before.size != byte_size:
            raise BlobIntegrityError(f"blob differs from its content identity: {digest}")
        observed = 0
        actual = hashlib.sha256()
        while block := os.read(descriptor, min(DEFAULT_READ_CHUNK_BYTES, byte_size - observed + 1)):
            observed += len(block)
            if observed > byte_size:
                raise BlobIntegrityError(f"blob grew beyond its content identity: {digest}")
            actual.update(block)
        after = LocalFileState.from_stat(os.fstat(descriptor))
        visible = LocalFileState.from_stat(os.stat(name, dir_fd=directory, follow_symlinks=False))
        if observed != byte_size or "sha256:" + actual.hexdigest() != digest or before != after or after != visible:
            raise BlobIntegrityError(f"blob differs from its content identity: {digest}")
    except FileNotFoundError as error:
        raise BlobIntegrityError(f"immutable blob disappeared: {digest}") from error
    finally:
        os.close(descriptor)


def _pending_file(directory: int) -> tuple[int, str]:
    for _ in range(128):
        name = f"blob-{secrets.token_hex(16)}"
        try:
            descriptor = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
                dir_fd=directory,
            )
        except FileExistsError:
            continue
        return descriptor, name
    raise BlobIntegrityError("blob pending name space is exhausted")


class LocalBlobWriter:
    """Conditionally store exact bytes under their qualified SHA-256 digest.

    The default layout is ``sha256/<hex>``. A consumer needing two-digit
    sharding selects ``object_prefix='objects/sha256', shard_digits=2``.
    ``create=False`` admits an existing root, prefix and .pending directory;
    put may still create a missing shard. The caller owns the input iterator,
    including closing it when a known, verified object bypasses consumption.
    """

    def __init__(
        self,
        root: Path,
        *,
        object_prefix: str = "sha256",
        shard_digits: int = 0,
        create: bool = True,
    ) -> None:
        prefix = validate_object_key(object_prefix, path="object_prefix")
        if prefix.split("/")[0] == ".pending":
            raise ValueError("object_prefix must not use the .pending staging directory")
        if isinstance(shard_digits, bool) or not isinstance(shard_digits, int) or shard_digits not in (0, 2):
            raise ValueError("shard_digits must be 0 or 2")
        selected = Path(root)
        if create:
            selected.mkdir(parents=True, exist_ok=True)
        try:
            self._pin = PinnedLocalDirectory(selected)
        except (ArtifactVerificationError, MemberSourceError) as error:
            raise ValueError("blob store root must be a present non-symlink directory") from error
        self.root = self._pin.path
        self.object_prefix = prefix
        self.shard_digits = shard_digits
        self._directories: dict[str, tuple[int, int]] = {}
        with self._layout(create=create):
            pass
        self._recheck()

    @contextmanager
    def _layout(self, *, create: bool = False) -> Iterator[tuple[int, int, int]]:
        with ExitStack() as stack:
            try:
                root = self._pin._open_pinned()
            except (ArtifactVerificationError, MemberSourceError) as error:
                raise ValueError(f"blob store root changed or is unavailable: {error}") from error
            stack.callback(os.close, root)
            prefix = root
            key = ""
            for name in self.object_prefix.split("/"):
                key = f"{key}/{name}".lstrip("/")
                child = _child(prefix, name, create=create)
                stack.callback(os.close, child)
                identity = _identity(child)
                expected = self._directories.setdefault(key, identity)
                if identity != expected:
                    raise ValueError(f"blob store directory changed after admission: {key}")
                prefix = child
            pending = _child(root, ".pending", create=create)
            stack.callback(os.close, pending)
            identity = _identity(pending)
            if identity != self._directories.setdefault(".pending", identity):
                raise ValueError("blob store pending directory changed after admission")
            yield root, prefix, pending

    def _recheck(self, shard: str = "", identity: tuple[int, int] | None = None) -> None:
        with self._layout() as (_, prefix, _):
            if shard:
                descriptor = _child(prefix, shard, create=False)
                try:
                    if _identity(descriptor) != identity:
                        raise ValueError("blob store shard changed during the write")
                finally:
                    os.close(descriptor)

    def _durable(
        self,
        root: int,
        prefix: int,
        destination: int,
        shard: str,
        identity: tuple[int, int] | None,
    ) -> None:
        self._recheck(shard, identity)
        os.fsync(destination)
        os.fsync(prefix)
        os.fsync(root)
        self._recheck(shard, identity)

    def put(
        self,
        chunks: Iterable[bytes],
        *,
        max_bytes: int,
        expected_digest: str | None = None,
        expected_size: int | None = None,
    ) -> LocalBlobWrite:
        """Hash and stage at most max_bytes; verify reuse instead of overwriting.

        A file changing during verification is refused, even if another writer
        only removed its temporary hardlink. Callers may retry that operation.
        """

        _nonnegative(max_bytes, "max_bytes")
        if expected_digest is not None:
            _digest(expected_digest, path="expected_digest")
        if expected_size is not None:
            _nonnegative(expected_size, "expected_size")
            if expected_size > max_bytes:
                raise BlobLimitError("expected_size exceeds the blob write limit")
        with self._layout() as (root, prefix, pending), ExitStack() as stack:
            shard = ""
            shard_identity = None
            destination = prefix

            def select_destination(digest: str) -> str:
                nonlocal destination, shard, shard_identity
                name = digest[7:]
                if self.shard_digits:
                    shard = name[: self.shard_digits]
                    destination = _child(prefix, shard, create=True)
                    stack.callback(os.close, destination)
                    shard_identity = _identity(destination)
                    expected = self._directories.setdefault(f"{self.object_prefix}/{shard}", shard_identity)
                    if shard_identity != expected:
                        raise ValueError("blob store shard changed after admission")
                return name

            name = select_destination(expected_digest) if expected_digest is not None else ""
            if expected_digest is not None and expected_size is not None and _exists(destination, name):
                _verify(destination, name, expected_digest, expected_size)
                self._durable(root, prefix, destination, shard, shard_identity)
                return LocalBlobWrite(
                    expected_digest,
                    f"{self.object_prefix}/{shard + '/' if shard else ''}{name}",
                    expected_size,
                    True,
                    0,
                )

            descriptor, pending_name = _pending_file(pending)
            staged_identity = _identity(descriptor)
            observed = 0
            digest = hashlib.sha256()
            try:
                for chunk in chunks:
                    self._recheck(shard, shard_identity)
                    if not isinstance(chunk, bytes):
                        raise TypeError("blob chunks must be bytes")
                    if len(chunk) > max_bytes - observed:
                        raise BlobLimitError(f"blob exceeds the {max_bytes}-byte write limit")
                    block = memoryview(chunk)
                    while block:
                        written = os.write(descriptor, block)
                        if written == 0:
                            raise OSError("blob staging write made no progress")
                        block = block[written:]
                    observed += len(chunk)
                    digest.update(chunk)
                self._recheck(shard, shard_identity)
                os.fsync(descriptor)
                actual = "sha256:" + digest.hexdigest()
                if (expected_digest is not None and actual != expected_digest) or (
                    expected_size is not None and observed != expected_size
                ):
                    raise BlobIntegrityError("blob write differs from its declared receipt")
                if not name:
                    name = select_destination(actual)
                self._recheck(shard, shard_identity)
                staged = os.stat(pending_name, dir_fd=pending, follow_symlinks=False)
                if not stat.S_ISREG(staged.st_mode) or (staged.st_dev, staged.st_ino) != staged_identity:
                    raise BlobIntegrityError("blob staging file changed during the write")
                reused = False
                try:
                    os.link(
                        pending_name,
                        name,
                        src_dir_fd=pending,
                        dst_dir_fd=destination,
                        follow_symlinks=False,
                    )
                except FileExistsError:
                    reused = True
                _verify(destination, name, actual, observed)
                self._durable(root, prefix, destination, shard, shard_identity)
            finally:
                os.close(descriptor)
                try:
                    os.unlink(pending_name, dir_fd=pending)
                except FileNotFoundError:
                    pass
                os.fsync(pending)
            self._recheck(shard, shard_identity)
            return LocalBlobWrite(
                actual,
                f"{self.object_prefix}/{shard + '/' if shard else ''}{name}",
                observed,
                reused,
                observed,
            )


__all__ = ["BlobIntegrityError", "BlobLimitError", "LocalBlobWrite", "LocalBlobWriter"]
