"""URI identity parity with the frozen loop and independent known answers."""

import unittest

from rulespec_projection import encode_for_uri, fragment_urn
from uri_encoding_oracle import encode_for_uri as old_encode_for_uri


class UriEncodingTests(unittest.TestCase):
    def test_known_answers(self) -> None:
        for value, expected in [
            ("", ""),
            ("AZaz09-._~", "AZaz09-._~"),
            ("%2F /?&=:#[]+", "%252F%20%2F%3F%26%3D%3A%23%5B%5D%2B"),
            ("é e\u0301 汉 😀", "%C3%A9%20e%CC%81%20%E6%B1%89%20%F0%9F%98%80"),
            ("\x00\t\n\r\x7f", "%00%09%0A%0D%7F"),
        ]:
            with self.subTest(value=value):
                self.assertEqual(encode_for_uri(value), expected)
                self.assertEqual(old_encode_for_uri(value), expected)

    def test_all_ascii_and_unicode_boundaries_keep_exact_output(self) -> None:
        values = [
            "".join(map(chr, range(128))),
            "\u007f\u0080\u07ff\u0800\ud7ff\ue000\uffff\U00010000\U0010ffff",
        ]
        for value in values:
            with self.subTest(value=repr(value)):
                self.assertEqual(encode_for_uri(value), old_encode_for_uri(value))

    def test_unicode_normalization_is_not_applied(self) -> None:
        self.assertNotEqual(encode_for_uri("é"), encode_for_uri("e\u0301"))

    def test_string_subclasses_remain_accepted(self) -> None:
        class SourceString(str):
            pass

        self.assertEqual(encode_for_uri(SourceString("a/b")), "a%2Fb")

    def test_surrogates_refuse_with_named_whole_string_diagnostics(self) -> None:
        for value in ["\ud800", "a\udfffz", "ab\ud800\udfff"]:
            with self.subTest(value=repr(value)):
                with self.assertRaises(UnicodeEncodeError) as old_error:
                    old_encode_for_uri(value)
                with self.assertRaises(UnicodeEncodeError) as new_error:
                    encode_for_uri(value)
                self.assertEqual(new_error.exception.object, value)
                self.assertEqual(old_error.exception.start, 0)
                self.assertEqual(
                    new_error.exception.start,
                    next(
                        i
                        for i, char in enumerate(value)
                        if 0xD800 <= ord(char) <= 0xDFFF
                    ),
                )

    def test_non_strings_remain_refused_with_stdlib_type_error(self) -> None:
        for value in [b"a/b", bytearray(b"a/b"), None, 1]:
            with self.subTest(value=value):
                with self.assertRaises((TypeError, AttributeError)):
                    old_encode_for_uri(value)
                with self.assertRaises(TypeError):
                    encode_for_uri(value)

    def test_incidental_iterable_inputs_now_refuse_at_the_string_boundary(self) -> None:
        for value, old_result in [
            (b"", ""),
            (bytearray(), ""),
            ([], ""),
            ((), ""),
            (["a", "/", "é"], "a%2F%C3%A9"),
            (("a", "/", "é"), "a%2F%C3%A9"),
        ]:
            with self.subTest(value=value):
                self.assertEqual(old_encode_for_uri(value), old_result)
                with self.assertRaises(TypeError):
                    encode_for_uri(value)

    def test_fragment_identity_includes_exact_old_encoded_source(self) -> None:
        source = "https://example.test/é?x=%2F&y=😀"
        digest = "a" * 64
        expected = f"urn:rkaf:fragment:{old_encode_for_uri(source)}:2:7:sha256-{digest}"
        self.assertEqual(fragment_urn(source, 2, 7, digest), expected)


if __name__ == "__main__":
    unittest.main()
