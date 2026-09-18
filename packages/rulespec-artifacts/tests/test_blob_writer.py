"""Bounded writes preserve exact bytes, safe paths, and conditional reuse."""

from __future__ import annotations

import hashlib
import os
import stat
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from rulespec_artifacts import BlobIntegrityError, BlobLimitError, LocalBlobWriter


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


class BlobWriterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "store"

    def test_computed_and_known_identity_in_both_layouts(self) -> None:
        payload = b"preserved source bytes"
        for prefix, shard in (("sha256", 0), ("objects/sha256", 2)):
            with self.subTest(prefix=prefix):
                writer = LocalBlobWriter(self.root / str(shard), object_prefix=prefix, shard_digits=shard)
                result = writer.put([payload[:3], b"", payload[3:]], max_bytes=len(payload))
                hex_digest = digest(payload)[7:]
                key = f"{prefix}/{hex_digest[:2] + '/' if shard else ''}{hex_digest}"
                self.assertEqual(
                    (result.digest, result.object_key, result.byte_size), (digest(payload), key, len(payload))
                )
                self.assertEqual((result.reused, result.bytes_written), (False, len(payload)))
                self.assertEqual((writer.root / key).read_bytes(), payload)

                def unavailable():
                    raise AssertionError("verified early reuse must not consume input")
                    yield b""

                reused = writer.put(
                    unavailable(), max_bytes=len(payload), expected_digest=digest(payload), expected_size=len(payload)
                )
                self.assertEqual((reused.reused, reused.bytes_written), (True, 0))
                self.assertEqual(list((writer.root / ".pending").iterdir()), [])

    def test_empty_blob_with_zero_bound(self) -> None:
        writer = LocalBlobWriter(self.root)
        result = writer.put([], max_bytes=0, expected_size=0)
        self.assertEqual((result.digest, result.byte_size, result.bytes_written), (digest(b""), 0, 0))
        self.assertEqual((self.root / result.object_key).read_bytes(), b"")

    def test_known_digest_without_size_still_consumes_and_checks_input(self) -> None:
        writer = LocalBlobWriter(self.root)
        writer.put([b"good"], max_bytes=4)
        with self.assertRaises(BlobIntegrityError):
            writer.put([b"wrong"], max_bytes=5, expected_digest=digest(b"good"))
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_bound_refuses_before_writing_the_overflow_chunk(self) -> None:
        writer = LocalBlobWriter(self.root)
        original = os.write
        writes = []

        def observe(descriptor, content):
            writes.append(bytes(content))
            return original(descriptor, content)

        with patch("rulespec_artifacts._blobs.os.write", side_effect=observe), self.assertRaises(BlobLimitError):
            writer.put([b"ok", b"too much"], max_bytes=3)
        self.assertEqual(writes, [b"ok"])
        self.assertEqual(list((self.root / ".pending").iterdir()), [])
        self.assertEqual(list((self.root / "sha256").iterdir()), [])

    def test_declared_size_over_bound_refuses_before_input_or_reuse(self) -> None:
        writer = LocalBlobWriter(self.root)
        writer.put([b"abc"], max_bytes=3)
        with patch("rulespec_artifacts._blobs._verify") as verification:
            with self.assertRaises(BlobLimitError):
                writer.put(None, max_bytes=2, expected_digest=digest(b"abc"), expected_size=3)
            verification.assert_not_called()

    def test_invalid_limits_and_layouts(self) -> None:
        writer = LocalBlobWriter(self.root)
        for value in (True, False, -1, 0.0, "1", None):
            with self.subTest(max_bytes=value), self.assertRaises(ValueError):
                writer.put(None, max_bytes=value)
        for value in (True, -1, 0.0, "1"):
            with self.subTest(expected_size=value), self.assertRaises(ValueError):
                writer.put(None, max_bytes=5, expected_size=value)
        for prefix in (".pending", ".pending/sha256", "../sha256", "/sha256", "a//b", "a\\b"):
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                LocalBlobWriter(self.root, object_prefix=prefix)
        for shard in (True, 0.0, 1, 3, -1):
            with self.subTest(shard=shard), self.assertRaises(ValueError):
                LocalBlobWriter(self.root, shard_digits=shard)

    def test_mismatched_digest_and_size_remove_staging(self) -> None:
        writer = LocalBlobWriter(self.root)
        for expected in ({"expected_digest": digest(b"other")}, {"expected_size": 3}):
            with self.subTest(expected=expected), self.assertRaises(BlobIntegrityError):
                writer.put([b"actual"], max_bytes=10, **expected)
            self.assertEqual(list((self.root / ".pending").iterdir()), [])
            self.assertEqual(list((self.root / "sha256").iterdir()), [])

    def test_corrupt_existing_object_is_never_reused(self) -> None:
        writer = LocalBlobWriter(self.root)
        result = writer.put([b"correct"], max_bytes=7)
        target = self.root / result.object_key
        for corruption in (b"badsize", b"short"):
            target.write_bytes(corruption)
            with self.subTest(corruption=corruption), self.assertRaises(BlobIntegrityError):
                writer.put([b"correct"], max_bytes=7, expected_digest=result.digest, expected_size=7)
            self.assertEqual(target.read_bytes(), corruption)

    def test_nonregular_existing_target_is_refused(self) -> None:
        writer = LocalBlobWriter(self.root)
        target = self.root / "sha256" / digest(b"a")[7:]
        sentinel = Path(self.temporary.name) / "sentinel"
        sentinel.write_bytes(b"outside")
        for kind in ("symlink", "directory", "fifo"):
            with self.subTest(kind=kind):
                if kind == "symlink":
                    target.symlink_to(sentinel)
                elif kind == "directory":
                    target.mkdir()
                else:
                    os.mkfifo(target)
                with self.assertRaises(BlobIntegrityError):
                    writer.put([b"a"], max_bytes=1, expected_digest=digest(b"a"), expected_size=1)
                target.rmdir() if kind == "directory" else target.unlink()
        self.assertEqual(sentinel.read_bytes(), b"outside")

    def test_eexist_race_verifies_winner_and_counts_staged_bytes(self) -> None:
        writer = LocalBlobWriter(self.root)
        payload = b"race winner"
        target = self.root / "sha256" / digest(payload)[7:]

        def race(*args, **kwargs):
            target.write_bytes(payload)
            raise FileExistsError("another publisher won")

        with patch("rulespec_artifacts._blobs.os.link", side_effect=race):
            result = writer.put([payload], max_bytes=len(payload))
        self.assertTrue(result.reused)
        self.assertEqual(result.bytes_written, len(payload))
        self.assertEqual(target.read_bytes(), payload)
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_corrupt_eexist_winner_is_preserved_and_refused(self) -> None:
        writer = LocalBlobWriter(self.root)
        target = self.root / "sha256" / digest(b"valid")[7:]

        def race(*args, **kwargs):
            target.write_bytes(b"wrong")
            raise FileExistsError("another publisher won")

        with patch("rulespec_artifacts._blobs.os.link", side_effect=race), self.assertRaises(BlobIntegrityError):
            writer.put([b"valid"], max_bytes=5)
        self.assertEqual(target.read_bytes(), b"wrong")
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_input_failure_cleans_staging_without_taking_iterator_ownership(self) -> None:
        writer = LocalBlobWriter(self.root)
        failure = RuntimeError("source stopped")

        class Input:
            closed = False

            def __iter__(self):
                yield b"before failure"
                raise failure

            def close(self):
                self.closed = True

        chunks = Input()
        with self.assertRaises(RuntimeError) as error:
            writer.put(chunks, max_bytes=100)
        self.assertIs(error.exception, failure)
        self.assertFalse(chunks.closed)
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_nonbytes_input_and_write_failure_clean_staging(self) -> None:
        writer = LocalBlobWriter(self.root)
        with self.assertRaises(TypeError):
            writer.put([bytearray(b"bad")], max_bytes=3)
        with patch("rulespec_artifacts._blobs.os.write", side_effect=OSError("disk full")), self.assertRaises(OSError):
            writer.put([b"a"], max_bytes=1)
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_partial_writes_preserve_the_complete_payload(self) -> None:
        writer = LocalBlobWriter(self.root)
        original = os.write

        def partial(descriptor, content):
            return original(descriptor, content[:2])

        with patch("rulespec_artifacts._blobs.os.write", side_effect=partial):
            result = writer.put([b"complete payload"], max_bytes=16)
        self.assertEqual((self.root / result.object_key).read_bytes(), b"complete payload")
        self.assertEqual(result.bytes_written, 16)

    def test_failed_data_flush_never_links_a_destination(self) -> None:
        writer = LocalBlobWriter(self.root)
        original = os.fsync

        def refuse_file(descriptor):
            if stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise OSError("data flush failed")
            original(descriptor)

        with patch("rulespec_artifacts._blobs.os.fsync", side_effect=refuse_file), self.assertRaises(OSError):
            writer.put([b"a"], max_bytes=1)
        self.assertEqual(list((self.root / ".pending").iterdir()), [])
        self.assertEqual(list((self.root / "sha256").iterdir()), [])

    def test_create_false_does_not_create_layout(self) -> None:
        self.root.mkdir()
        with self.assertRaises(ValueError):
            LocalBlobWriter(self.root, create=False)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_symlink_layout_is_refused_without_writing_outside(self) -> None:
        for key in ("root", "objects", "objects/sha256", ".pending"):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "store"
                outside = Path(directory) / "outside"
                outside.mkdir()
                target = root if key == "root" else root / key
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError):
                    LocalBlobWriter(root, object_prefix="objects/sha256", shard_digits=2)
                self.assertEqual(list(outside.iterdir()), [])

    def test_stream_callback_directory_replacement_fails_closed(self) -> None:
        for key in ("root", "objects", "objects/sha256", ".pending", "objects/sha256/ca"):
            for symlink in (False, True):
                for at_end in (False, True):
                    with (
                        self.subTest(key=key, symlink=symlink, at_end=at_end),
                        tempfile.TemporaryDirectory() as directory,
                    ):
                        root = Path(directory) / "store"
                        writer = LocalBlobWriter(root, object_prefix="objects/sha256", shard_digits=2)
                        # sha256(b'a') begins ca: the expected digest pins this shard before input.
                        target = root if key == "root" else root / key
                        retained = Path(directory) / "retained"
                        outside = Path(directory) / "outside"
                        outside.mkdir()

                        def replace(target=target, retained=retained, outside=outside, symlink=symlink):
                            target.rename(retained)
                            target.symlink_to(outside, target_is_directory=True) if symlink else target.mkdir()

                        def chunks(at_end=at_end, replace=replace):
                            if not at_end:
                                replace()
                            yield b"a"
                            if at_end:
                                replace()

                        with self.assertRaises(ValueError):
                            writer.put(chunks(), max_bytes=1, expected_digest=digest(b"a"), expected_size=1)
                        pending = (
                            retained / ".pending"
                            if key == "root"
                            else retained
                            if key == ".pending"
                            else root / ".pending"
                        )
                        self.assertEqual(list(pending.iterdir()), [])
                        self.assertEqual(list(outside.iterdir()), [])

    def test_directory_replacement_during_link_is_detected(self) -> None:
        writer = LocalBlobWriter(self.root)
        original = os.link

        def replace(*args, **kwargs):
            (self.root / "sha256").rename(self.root / "retained")
            (self.root / "sha256").mkdir()
            return original(*args, **kwargs)

        with patch("rulespec_artifacts._blobs.os.link", side_effect=replace), self.assertRaises(ValueError):
            writer.put([b"a"], max_bytes=1)
        self.assertEqual(list((self.root / "sha256").iterdir()), [])
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_used_shard_replacement_between_puts_is_refused(self) -> None:
        for symlink in (False, True):
            for known in (False, True):
                with self.subTest(symlink=symlink, known=known), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory) / "store"
                    writer = LocalBlobWriter(root, object_prefix="objects/sha256", shard_digits=2)
                    original = writer.put([b"a"], max_bytes=1)
                    shard = root / "objects/sha256/ca"
                    retained = Path(directory) / "retained"
                    outside = Path(directory) / "outside"
                    outside.mkdir()
                    shard.rename(retained)
                    shard.symlink_to(outside, target_is_directory=True) if symlink else shard.mkdir()
                    expected = {"expected_digest": original.digest, "expected_size": 1} if known else {}
                    with self.assertRaises(ValueError):
                        writer.put([b"a"], max_bytes=1, **expected)
                    self.assertEqual((retained / original.digest[7:]).read_bytes(), b"a")
                    self.assertEqual(list((root / ".pending").iterdir()), [])
                    self.assertEqual(list(outside.iterdir()), [])

    def test_early_reuse_requires_directory_durability(self) -> None:
        writer = LocalBlobWriter(self.root)
        writer.put([b"a"], max_bytes=1)
        with (
            patch("rulespec_artifacts._blobs.os.fsync", side_effect=OSError("directory sync failed")),
            self.assertRaises(OSError),
        ):
            writer.put(None, max_bytes=1, expected_digest=digest(b"a"), expected_size=1)
        self.assertEqual((self.root / "sha256" / digest(b"a")[7:]).read_bytes(), b"a")
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_directory_replacement_during_sync_is_detected_in_both_success_paths(self) -> None:
        for reuse in (False, True):
            with self.subTest(reuse=reuse), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "store"
                writer = LocalBlobWriter(root)
                if reuse:
                    writer.put([b"a"], max_bytes=1)
                original = os.fsync
                changed = []

                def replace(descriptor, root=root, changed=changed, original=original):
                    if not changed and stat.S_ISDIR(os.fstat(descriptor).st_mode):
                        (root / "sha256").rename(root / "retained")
                        (root / "sha256").mkdir()
                        changed.append(True)
                    original(descriptor)

                with patch("rulespec_artifacts._blobs.os.fsync", side_effect=replace), self.assertRaises(ValueError):
                    writer.put(None if reuse else [b"a"], max_bytes=1, expected_digest=digest(b"a"), expected_size=1)
                self.assertEqual(list((root / "sha256").iterdir()), [])
                self.assertEqual(list((root / ".pending").iterdir()), [])

    def test_directory_replacement_during_final_pending_sync_is_detected(self) -> None:
        writer = LocalBlobWriter(self.root)
        pending_identity = (self.root / ".pending").stat().st_ino
        original = os.fsync

        def replace_on_cleanup(descriptor):
            if os.fstat(descriptor).st_ino == pending_identity:
                (self.root / "sha256").rename(self.root / "retained")
                (self.root / "sha256").mkdir()
            original(descriptor)

        with patch("rulespec_artifacts._blobs.os.fsync", side_effect=replace_on_cleanup), self.assertRaises(ValueError):
            writer.put([b"a"], max_bytes=1)
        self.assertEqual(list((self.root / "sha256").iterdir()), [])
        self.assertEqual(list((self.root / ".pending").iterdir()), [])

    def test_same_content_concurrent_reuse_survives_the_winners_pending_link_cleanup(self) -> None:
        # DocSpec's 2026-09-12 probe: writer A publishes and pauses before unlinking its
        # pending hardlink; writer B captures its first file state; A unlinks; B reads
        # unchanged bytes whose ctime moved. Synchronized on the writers' own IO calls.
        payload = b"same immutable bytes"
        first = LocalBlobWriter(self.root, object_prefix="objects/sha256", shard_digits=2)
        second = LocalBlobWriter(self.root, object_prefix="objects/sha256", shard_digits=2)
        winner_at_cleanup, allow_cleanup, winner_finished = threading.Event(), threading.Event(), threading.Event()
        current = threading.local()
        original_unlink, original_read = os.unlink, os.read

        def unlink(name, *args, **kwargs):
            if getattr(current, "role", None) == "winner" and kwargs.get("dir_fd") is not None:
                winner_at_cleanup.set()
                self.assertTrue(allow_cleanup.wait(10), "second writer never reached verification")
            return original_unlink(name, *args, **kwargs)

        def read(descriptor, size):
            if getattr(current, "role", None) == "reuse" and not current.released:
                current.released = True  # the verifier has captured its before-state here
                allow_cleanup.set()
                self.assertTrue(winner_finished.wait(10), "winner cleanup did not finish")
            return original_read(descriptor, size)

        def winner():
            current.role = "winner"
            try:
                return first.put((payload,), max_bytes=len(payload))
            finally:
                winner_finished.set()

        def reuse():
            current.role, current.released = "reuse", False
            return second.put((), max_bytes=len(payload), expected_digest=digest(payload), expected_size=len(payload))

        with (
            patch("rulespec_artifacts._blobs.os.unlink", side_effect=unlink),
            patch("rulespec_artifacts._blobs.os.read", side_effect=read),
            ThreadPoolExecutor(max_workers=2) as workers,
        ):
            written = workers.submit(winner)
            try:
                self.assertTrue(winner_at_cleanup.wait(10), "winner never published the blob")
                reused = workers.submit(reuse)
                published = written.result(timeout=15)
                self.assertEqual((self.root / published.object_key).read_bytes(), payload)
                self.assertEqual(list((self.root / ".pending").iterdir()), [])
                verified = reused.result(timeout=15)
            finally:
                allow_cleanup.set()
        self.assertEqual((verified.reused, verified.digest, verified.bytes_written), (True, published.digest, 0))

    def _touch_ctime(self, target: Path) -> None:
        # A hardlink added and removed moves ctime and link count and no byte.
        link = target.with_name(target.name + ".link")
        os.link(target, link)
        os.unlink(link)

    def test_ctime_or_mode_only_change_during_verification_is_reverified_not_refused(self) -> None:
        writer = LocalBlobWriter(self.root)
        payload = b"unchanged bytes"
        result = writer.put([payload], max_bytes=len(payload))
        target = self.root / result.object_key
        for disturb in (self._touch_ctime, lambda path: os.chmod(path, 0o444)):
            with self.subTest(disturb=disturb.__name__ if hasattr(disturb, "__name__") else "chmod"):
                original, passes = os.read, []

                def read(descriptor, size, disturb=disturb, passes=passes):
                    block = original(descriptor, size)
                    if not block:
                        passes.append(True)
                        if len(passes) == 1:
                            disturb(target)
                    return block

                with patch("rulespec_artifacts._blobs.os.read", side_effect=read):
                    reused = writer.put(None, max_bytes=len(payload), expected_digest=result.digest, expected_size=len(payload))
                self.assertTrue(reused.reused)
                self.assertGreaterEqual(len(passes), 2, "a ctime-only move must trigger a second read")
        self.assertEqual(target.read_bytes(), payload)

    def test_rewrite_that_restores_mtime_after_the_read_is_refused(self) -> None:
        writer = LocalBlobWriter(self.root)
        payload = b"original bytes"
        result = writer.put([payload], max_bytes=len(payload))
        target = self.root / result.object_key
        original, rewritten = os.read, []

        def read(descriptor, size):
            block = original(descriptor, size)
            if not block and not rewritten:
                # Same inode, same size, mtime put back: only ctime betrays it.
                state = target.stat()
                with open(target, "r+b") as handle:
                    handle.write(b"replaced bytes")
                os.utime(target, ns=(state.st_atime_ns, state.st_mtime_ns))
                rewritten.append(True)
            return block

        with patch("rulespec_artifacts._blobs.os.read", side_effect=read), self.assertRaises(BlobIntegrityError):
            writer.put(None, max_bytes=len(payload), expected_digest=result.digest, expected_size=len(payload))
        self.assertEqual(target.read_bytes(), b"replaced bytes")

    def test_a_blob_that_keeps_changing_is_refused_after_a_bounded_number_of_passes(self) -> None:
        writer = LocalBlobWriter(self.root)
        payload = b"restless"
        result = writer.put([payload], max_bytes=len(payload))
        target = self.root / result.object_key
        original, passes = os.read, []

        def read(descriptor, size):
            block = original(descriptor, size)
            if not block:
                passes.append(True)
                self._touch_ctime(target)
            return block

        with patch("rulespec_artifacts._blobs.os.read", side_effect=read), self.assertRaises(BlobIntegrityError) as error:
            writer.put(None, max_bytes=len(payload), expected_digest=result.digest, expected_size=len(payload))
        self.assertIn("kept changing", str(error.exception))
        self.assertEqual(len(passes), 3)
        self.assertEqual(target.read_bytes(), payload)

    def test_expected_root_pins_the_admitted_directory_before_any_write(self) -> None:
        self.root.mkdir()
        state = self.root.stat()
        identity = (state.st_dev, state.st_ino)
        writer = LocalBlobWriter(self.root, expected_root=identity)
        self.assertEqual(writer.root_identity, identity)
        self.assertEqual(writer.put([b"a"], max_bytes=1).reused, False)

        untouched = Path(self.temporary.name) / "untouched"
        untouched.mkdir()
        with self.assertRaises(ValueError):
            LocalBlobWriter(untouched, expected_root=(identity[0], identity[1] + 1))
        self.assertEqual(list(untouched.iterdir()), [], "a wrong identity must be refused before any layout write")

        replaced = Path(self.temporary.name) / "replaced"
        replaced.mkdir()
        admitted = (replaced.stat().st_dev, replaced.stat().st_ino)
        replaced.rename(Path(self.temporary.name) / "moved-away")
        replaced.mkdir()
        with self.assertRaises(ValueError):
            LocalBlobWriter(replaced, expected_root=admitted)
        self.assertEqual(list(replaced.iterdir()), [])

        missing = Path(self.temporary.name) / "missing"
        with self.assertRaises(ValueError):
            LocalBlobWriter(missing, expected_root=identity)
        self.assertFalse(missing.exists(), "an expected identity never creates the root")

        for bad in ((1,), (1, 2, 3), (True, 1), ("1", 2), [1, 2]):
            with self.subTest(expected_root=bad), self.assertRaises(ValueError):
                LocalBlobWriter(self.root, expected_root=bad)


if __name__ == "__main__":
    unittest.main()
