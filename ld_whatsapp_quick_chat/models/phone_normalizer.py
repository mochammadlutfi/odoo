"""Indonesian-first phone normalizer for WhatsApp.

Used as a stateless helper — no Odoo model. Exposed via PhoneNormalizer class.
"""
import re
import urllib.parse


class PhoneNormalizer:
    """Normalize Indonesian phone numbers to WhatsApp wa.me format.

    Rules:
    - Leading "0"  -> replace with "62"
    - Leading "8"  -> prepend "62" (bare mobile without 0/62)
    - Leading "62" -> keep
    - Otherwise    -> keep (international numbers untouched)

    Length constraint after normalization: 10..15 digits.
    """

    MIN_LEN = 10
    MAX_LEN = 15

    @staticmethod
    def normalize(phone):
        """Return normalized digits-only string, or None if invalid."""
        if not phone:
            return None

        digits = re.sub(r"\D", "", str(phone))
        if not digits:
            return None

        if digits.startswith("0"):
            digits = "62" + digits[1:]
        elif digits.startswith("8"):
            digits = "62" + digits
        # else: already starts with 62 or international -> keep as-is

        if len(digits) < PhoneNormalizer.MIN_LEN or len(digits) > PhoneNormalizer.MAX_LEN:
            return None

        return digits

    @staticmethod
    def to_wa_url(phone, message=""):
        """Build wa.me URL. Returns None if phone invalid."""
        normalized = PhoneNormalizer.normalize(phone)
        if not normalized:
            return None
        encoded = urllib.parse.quote(message or "")
        return f"https://wa.me/{normalized}?text={encoded}"

    @staticmethod
    def is_valid(phone):
        return PhoneNormalizer.normalize(phone) is not None
