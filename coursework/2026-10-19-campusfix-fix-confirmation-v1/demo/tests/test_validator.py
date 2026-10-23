import unittest

from validator import Validate


class ValidateTests(unittest.TestCase):
    def assertAccepted(self, value, expected):
        result = Validate(value)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.normalized_description, expected)
        self.assertIsNone(result.error_code)

    def assertRejected(self, value, error):
        result = Validate(value)
        self.assertFalse(result.is_valid, "Input outside the accepted description domain")
        self.assertEqual(result.error_code, error)
        self.assertIsNone(result.normalized_description)

    def test_accepts_one_character(self):
        self.assertAccepted("a", "a")

    def test_accepts_normal_text(self):
        text = "Лампа в аудитории не работает."
        self.assertAccepted(text, text)

    def test_accepts_999_characters(self):
        self.assertAccepted("a" * 999, "a" * 999)

    def test_accepts_1000_characters(self):
        self.assertAccepted("a" * 1000, "a" * 1000)

    def test_tc_cf_05_rejects_1001_characters(self):
        self.assertRejected("a" * 1001, "DESCRIPTION_TOO_LONG")

    def test_rejects_1002_characters(self):
        self.assertRejected("a" * 1002, "DESCRIPTION_TOO_LONG")

    def test_rejects_5000_characters(self):
        self.assertRejected("a" * 5000, "DESCRIPTION_TOO_LONG")

    def test_rejects_empty_string(self):
        self.assertRejected("", "DESCRIPTION_REQUIRED")

    def test_rejects_spaces_only(self):
        self.assertRejected("   ", "DESCRIPTION_REQUIRED")

    def test_rejects_tabs_and_newlines_only(self):
        self.assertRejected("\t\n\r  ", "DESCRIPTION_REQUIRED")

    def test_rejects_none(self):
        self.assertRejected(None, "DESCRIPTION_TYPE")

    def test_rejects_integer(self):
        self.assertRejected(1001, "DESCRIPTION_TYPE")

    def test_rejects_bytes(self):
        self.assertRejected(b"description", "DESCRIPTION_TYPE")

    def test_accepts_1000_chinese_characters(self):
        self.assertAccepted("中" * 1000, "中" * 1000)

    def test_accepts_1000_cyrillic_characters(self):
        self.assertAccepted("я" * 1000, "я" * 1000)

    def test_trims_outer_whitespace_before_length_check(self):
        self.assertAccepted(" \t" + "a" * 1000 + "\n ", "a" * 1000)

    def test_preserves_internal_whitespace(self):
        self.assertAccepted("  a  b\nc  ", "a  b\nc")

    def test_rejects_1002_characters_after_trimming(self):
        self.assertRejected("  " + "a" * 1002 + "  ", "DESCRIPTION_TOO_LONG")


if __name__ == "__main__":
    unittest.main()
