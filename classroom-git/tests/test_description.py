import unittest
from exercise import validate_description


class DescriptionTests(unittest.TestCase):
    def test_boundaries(self):
        for length in (10, 500):
            with self.subTest(length=length):
                self.assertEqual(validate_description("x" * length), "x" * length)

    def test_invalid_lengths(self):
        for value in ("", " " * 20, "x" * 9, "x" * 501):
            with self.subTest(length=len(value)):
                with self.assertRaises(ValueError):
                    validate_description(value)

    def test_whitespace_is_trimmed_before_counting(self):
        self.assertEqual(validate_description("  " + "x" * 10 + "\n"), "x" * 10)
        with self.assertRaises(ValueError):
            validate_description(" " + "x" * 9 + " ")

    def test_non_strings(self):
        for value in (None, 10, True, [], b"abcdefghij"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    validate_description(value)

    def test_multilingual_text(self):
        for value in ("中" * 10, "Описание заявки"):
            self.assertEqual(validate_description(value), value)
