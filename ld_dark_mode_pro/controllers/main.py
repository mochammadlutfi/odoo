from odoo import http
from odoo.http import request


VALID_COOKIE_MODES = ('light', 'dark')


class DarkModeController(http.Controller):

    @http.route('/ld_dark_mode/set', type='json', auth='user', methods=['POST'])
    def set_color_scheme(self, mode=None):
        """Set the `color_scheme` cookie used by Odoo 18 core to select the
        dark asset bundle. Also persists the user's `dark_mode_preference`
        so the choice survives cookie loss.

        Returns {'ok': True, 'mode': <mode>} or raises a ValueError mapped
        to a JSON-RPC error when input is invalid.
        """
        if mode not in VALID_COOKIE_MODES:
            raise ValueError(
                "Invalid dark mode value; expected one of %s."
                % (VALID_COOKIE_MODES,)
            )
        request.future_response.set_cookie(
            'color_scheme',
            mode,
            max_age=60 * 60 * 24 * 365,
            httponly=False,
            secure=request.httprequest.is_secure,
            samesite='Lax',
        )
        user = request.env.user
        pref = 'dark' if mode == 'dark' else 'light'
        if user.dark_mode_preference not in ('auto', 'schedule'):
            # dark_mode_preference is in SELF_WRITEABLE_FIELDS — no sudo needed.
            user.write({'dark_mode_preference': pref})
        return {'ok': True, 'mode': mode}

    @http.route('/ld_dark_mode/clear', type='json', auth='user', methods=['POST'])
    def clear_color_scheme(self):
        """Clear the color_scheme cookie so Odoo falls back to the light
        bundle. Used when switching to 'auto' or 'schedule' where the
        client-side JS will re-set the cookie as needed on the next tick.
        """
        request.future_response.set_cookie(
            'color_scheme',
            '',
            max_age=0,
            secure=request.httprequest.is_secure,
            samesite='Lax',
        )
        return {'ok': True}
