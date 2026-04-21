import base64
import logging
from io import BytesIO

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

BADGE_COLORS = {
    'production': (239, 68, 68),    # Red
    'staging': (245, 158, 11),      # Amber
    'uat': (168, 85, 247),          # Purple
    'dev': (59, 130, 246),          # Blue
}


class ResCompany(models.Model):
    _inherit = 'res.company'

    favicon = fields.Binary(string='Favicon', attachment=True)
    favicon_version = fields.Char(string='Favicon Version', compute='_compute_favicon_version', store=False)
    favicon_auto_generated = fields.Boolean(string='Auto-generate from Logo', default=True)
    favicon_environment_badge = fields.Selection([
        ('none', 'None'),
        ('auto', 'Auto (sync with ribbon config)'),
    ], string='Environment Badge', default='auto')
    apple_touch_icon = fields.Binary(string='Apple Touch Icon (180x180)', attachment=True)
    android_icon_192 = fields.Binary(string='Android Icon 192x192', attachment=True)
    android_icon_512 = fields.Binary(string='Android Icon 512x512', attachment=True)

    @api.depends('favicon')
    def _compute_favicon_version(self):
        import time
        for company in self:
            company.favicon_version = str(int(time.time()))

    def generate_favicon_from_logo(self):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            raise UserError(
                _('Pillow library is required. Install with: pip install Pillow')
            )

        for company in self:
            if not company.logo:
                continue

            logo_data = base64.b64decode(company.logo)
            img = Image.open(BytesIO(logo_data)).convert('RGBA')

            img = self._crop_to_square(img)

            badge_color = None
            if company.favicon_environment_badge == 'auto':
                env_param = self.env['ir.config_parameter'].sudo().get_param('ribbon_environment', False)
                if env_param:
                    badge_color = BADGE_COLORS.get(env_param)

            # Generate favicon.ico (16x16 + 32x32)
            ico_img = img.copy().resize((32, 32), Image.LANCZOS)
            if badge_color:
                ico_img = self._add_environment_badge(ico_img, badge_color, 32)

            buffer = BytesIO()
            ico_img.save(buffer, format='ICO', sizes=[(16, 16), (32, 32)])
            company.favicon = base64.b64encode(buffer.getvalue())

            # Generate apple-touch-icon.png (180x180)
            apple_img = img.copy().resize((180, 180), Image.LANCZOS)
            buffer = BytesIO()
            apple_img.save(buffer, format='PNG')
            company.apple_touch_icon = base64.b64encode(buffer.getvalue())

            # Generate android-chrome-192x192.png
            android_192 = img.copy().resize((192, 192), Image.LANCZOS)
            buffer = BytesIO()
            android_192.save(buffer, format='PNG')
            company.android_icon_192 = base64.b64encode(buffer.getvalue())

            # Generate android-chrome-512x512.png
            android_512 = img.copy().resize((512, 512), Image.LANCZOS)
            buffer = BytesIO()
            android_512.save(buffer, format='PNG')
            company.android_icon_512 = base64.b64encode(buffer.getvalue())

        return True

    def _crop_to_square(self, img):
        width, height = img.size
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        return img.crop((left, top, left + size, top + size))

    def _add_environment_badge(self, img, color, icon_size):
        try:
            from PIL import ImageDraw
        except ImportError:
            return img

        draw = ImageDraw.Draw(img)
        dot_size = max(4, icon_size // 4)
        x0 = icon_size - dot_size
        y0 = 0
        x1 = icon_size
        y1 = dot_size
        draw.ellipse([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=(255, 255, 255, 255))
        draw.ellipse([x0, y0, x1, y1], fill=(*color, 255))
        return img

    @api.model
    def get_favicon_preview_data(self, company_id):
        company = self.browse(company_id)
        if not company.logo:
            return {'error': _('No company logo found')}

        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return {'error': _('Pillow not installed')}

        logo_data = base64.b64decode(company.logo)
        img = Image.open(BytesIO(logo_data)).convert('RGBA')
        img = company._crop_to_square(img)

        badge_color = None
        if company.favicon_environment_badge == 'auto':
            env_param = self.env['ir.config_parameter'].sudo().get_param('ribbon_environment', False)
            if env_param:
                badge_color = BADGE_COLORS.get(env_param)

        previews = {}
        for size in [16, 32, 180]:
            resized = img.copy().resize((size, size), Image.LANCZOS)
            if badge_color and size in (16, 32):
                resized = company._add_environment_badge(resized, badge_color, size)
            buf = BytesIO()
            resized.save(buf, format='PNG')
            previews[f'{size}x{size}'] = base64.b64encode(buf.getvalue()).decode()

        return {'previews': previews}

    def action_generate_favicon(self):
        self.generate_favicon_from_logo()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Favicon Generated'),
                'message': _('Favicon successfully generated from company logo.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_clear_favicon(self):
        self.write({
            'favicon': False,
            'apple_touch_icon': False,
            'android_icon_192': False,
            'android_icon_512': False,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Favicon Cleared'),
                'message': _('Favicon cache cleared. Browser will reload the new favicon.'),
                'type': 'info',
                'sticky': False,
            }
        }

    @api.onchange('logo')
    def _onchange_logo_generate_favicon(self):
        if self.logo and self.favicon_auto_generated:
            try:
                self.generate_favicon_from_logo()
            except Exception as e:
                _logger.warning('Auto-generate favicon failed: %s', e)
