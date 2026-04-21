from odoo.tests import TransactionCase, tagged

from ..models.phone_normalizer import PhoneNormalizer


@tagged("post_install", "-at_install")
class TestPhoneNormalizer(TransactionCase):
    """Normalization matrix covering TEST-01..TEST-06 from the PRD."""

    def test_dash_separated_0_prefix(self):
        # "0812-3456-7890" -> "6281234567890"
        self.assertEqual(PhoneNormalizer.normalize("0812-3456-7890"), "6281234567890")

    def test_plus62_spaces(self):
        self.assertEqual(
            PhoneNormalizer.normalize("+62 812 3456 7890"), "6281234567890"
        )

    def test_62_no_plus_spaces(self):
        self.assertEqual(PhoneNormalizer.normalize("62812 3456 7890"), "6281234567890")

    def test_bare_8_prefix(self):
        self.assertEqual(PhoneNormalizer.normalize("812 3456 7890"), "6281234567890")

    def test_short_bare_8_prefix(self):
        self.assertEqual(PhoneNormalizer.normalize("8123456789"), "628123456789")

    def test_too_short_invalid(self):
        self.assertIsNone(PhoneNormalizer.normalize("12345"))

    def test_too_long_invalid(self):
        self.assertIsNone(PhoneNormalizer.normalize("1234567890123456789"))

    def test_empty_invalid(self):
        self.assertIsNone(PhoneNormalizer.normalize(""))
        self.assertIsNone(PhoneNormalizer.normalize(None))

    def test_letters_stripped(self):
        self.assertEqual(
            PhoneNormalizer.normalize("HP: 0812-3456-7890"), "6281234567890"
        )

    def test_to_wa_url_valid(self):
        url = PhoneNormalizer.to_wa_url("08123456789", "Hello")
        self.assertIsNotNone(url)
        self.assertIn("wa.me/628123456789", url)
        self.assertIn("text=Hello", url)

    def test_to_wa_url_encoded_special(self):
        url = PhoneNormalizer.to_wa_url("08123456789", "Halo, Bapak Budi!")
        self.assertIn("Halo%2C%20Bapak%20Budi%21", url)

    def test_to_wa_url_invalid_phone(self):
        self.assertIsNone(PhoneNormalizer.to_wa_url("123", "msg"))

    def test_is_valid(self):
        self.assertTrue(PhoneNormalizer.is_valid("08123456789"))
        self.assertFalse(PhoneNormalizer.is_valid("abc"))
