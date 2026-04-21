import base64
from io import BytesIO
from unittest.mock import patch

from odoo.tests.common import TransactionCase


def _create_dummy_logo():
    """Create minimal 64x64 red PNG for testing."""
    try:
        from PIL import Image
        img = Image.new('RGBA', (64, 64), color=(255, 0, 0, 255))
        buf = BytesIO()
        img.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue())
    except ImportError:
        return False


class TestFaviconGeneration(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.company

    def test_generate_favicon_from_logo(self):
        """TEST-01: Upload logo → auto-generate favicon works"""
        logo = _create_dummy_logo()
        if not logo:
            self.skipTest('Pillow not installed')

        self.company.logo = logo
        self.company.generate_favicon_from_logo()

        self.assertTrue(self.company.favicon, 'Favicon should be generated')
        self.assertTrue(self.company.apple_touch_icon, 'Apple touch icon should be generated')
        self.assertTrue(self.company.android_icon_192, 'Android 192 icon should be generated')
        self.assertTrue(self.company.android_icon_512, 'Android 512 icon should be generated')

    def test_favicon_is_valid_ico(self):
        """TEST-01b: Generated favicon is valid ICO format"""
        logo = _create_dummy_logo()
        if not logo:
            self.skipTest('Pillow not installed')

        self.company.logo = logo
        self.company.generate_favicon_from_logo()

        favicon_data = base64.b64decode(self.company.favicon)
        # ICO magic bytes: 00 00 01 00
        self.assertEqual(favicon_data[:4], b'\x00\x00\x01\x00', 'Should be valid ICO format')

    def test_multi_company_independent_favicon(self):
        """TEST-03: Multi-company: per company favicon independent"""
        logo1 = _create_dummy_logo()
        if not logo1:
            self.skipTest('Pillow not installed')

        company2 = self.env['res.company'].create({
            'name': 'Test Company 2',
            'logo': logo1,
        })

        # Generate for company 1
        self.company.logo = logo1
        self.company.generate_favicon_from_logo()

        # Generate for company 2 with different logo
        from PIL import Image
        img2 = Image.new('RGBA', (64, 64), color=(0, 0, 255, 255))  # Blue
        buf2 = BytesIO()
        img2.save(buf2, format='PNG')
        logo2 = base64.b64encode(buf2.getvalue())
        company2.logo = logo2
        company2.generate_favicon_from_logo()

        self.assertNotEqual(
            self.company.favicon, company2.favicon,
            'Each company should have independent favicon'
        )

    def test_crop_to_square_landscape(self):
        """TEST-11: Logo landscape → crop to square (center)"""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Pillow not installed')

        # Create 128x64 landscape image
        img = Image.new('RGBA', (128, 64), color=(0, 255, 0, 255))
        result = self.company._crop_to_square(img)

        self.assertEqual(result.width, result.height, 'Result should be square')
        self.assertEqual(result.width, 64, 'Square size should be min(128, 64)')

    def test_no_favicon_without_logo(self):
        """Favicon generation skipped when no logo"""
        self.company.logo = False
        self.company.generate_favicon_from_logo()
        # Should not raise, favicon stays False

    def test_environment_badge_auto(self):
        """TEST-05: Environment badge: dot visible di corner"""
        logo = _create_dummy_logo()
        if not logo:
            self.skipTest('Pillow not installed')

        self.env['ir.config_parameter'].sudo().set_param('ribbon_environment', 'production')

        self.company.logo = logo
        self.company.favicon_environment_badge = 'auto'
        self.company.generate_favicon_from_logo()

        self.assertTrue(self.company.favicon, 'Favicon with badge should be generated')

    def test_clear_favicon(self):
        """TEST-08: Clear favicon resets all icons"""
        logo = _create_dummy_logo()
        if not logo:
            self.skipTest('Pillow not installed')

        self.company.logo = logo
        self.company.generate_favicon_from_logo()
        self.assertTrue(self.company.favicon)

        self.company.action_clear_favicon()
        self.assertFalse(self.company.favicon)
        self.assertFalse(self.company.apple_touch_icon)
        self.assertFalse(self.company.android_icon_192)
        self.assertFalse(self.company.android_icon_512)

    def test_get_favicon_preview_data(self):
        """TEST-09: Preview data returns base64 PNG for each size"""
        logo = _create_dummy_logo()
        if not logo:
            self.skipTest('Pillow not installed')

        self.company.logo = logo
        result = self.env['res.company'].get_favicon_preview_data(self.company.id)

        self.assertIn('previews', result)
        self.assertIn('16x16', result['previews'])
        self.assertIn('32x32', result['previews'])
        self.assertIn('180x180', result['previews'])

    def test_preview_no_logo_returns_error(self):
        """Preview returns error dict when no logo"""
        self.company.logo = False
        result = self.env['res.company'].get_favicon_preview_data(self.company.id)
        self.assertIn('error', result)
