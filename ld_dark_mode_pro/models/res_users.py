from odoo import api, fields, models
from odoo.exceptions import ValidationError


DARK_MODE_CHOICES = [
    ('light', 'Light Mode'),
    ('dark', 'Dark Mode'),
    ('auto', 'Auto (Follow OS)'),
    ('schedule', 'Schedule'),
]


def _is_within_schedule(now_hour, start, end):
    """Pure function: return True if `now_hour` falls inside [start, end)
    on a 24h float clock. Handles wrap-around (end < start means overnight).

    - now_hour, start, end: float hours in [0.0, 24.0)
    - If start == end, schedule covers zero time -> False.
    """
    if start == end:
        return False
    if start < end:
        return start <= now_hour < end
    # Wrap-around, e.g. 19.0 -> 7.0 means 19-24 OR 0-7
    return now_hour >= start or now_hour < end


class ResUsers(models.Model):
    _inherit = 'res.users'

    dark_mode_preference = fields.Selection(
        DARK_MODE_CHOICES,
        string='Dark Mode',
        default='auto',
        help='Controls how the UI theme is chosen. '
             '"Auto" follows the OS preference; "Schedule" toggles on a '
             'time range set below.',
    )
    dark_mode_schedule_start = fields.Float(
        string='Dark Mode Start',
        default=19.0,
        help='Hour (24h, float) when dark mode activates in Schedule mode. '
             'Example: 19.5 means 19:30.',
    )
    dark_mode_schedule_end = fields.Float(
        string='Dark Mode End',
        default=7.0,
        help='Hour (24h, float) when dark mode deactivates in Schedule mode.',
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'dark_mode_preference',
            'dark_mode_schedule_start',
            'dark_mode_schedule_end',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            'dark_mode_preference',
            'dark_mode_schedule_start',
            'dark_mode_schedule_end',
        ]

    def _resolve_effective_dark_mode(self, now_hour=None, os_prefers_dark=False):
        """Return 'light' or 'dark' given the user's preference and clock/OS hints.

        - now_hour: float in [0, 24) representing local hour; required for 'schedule'.
        - os_prefers_dark: bool, client-side `prefers-color-scheme: dark` signal.

        This is a pure resolver usable from tests and from the controller during
        login flicker prevention.
        """
        self.ensure_one()
        pref = self.dark_mode_preference or 'auto'
        if pref == 'light':
            return 'light'
        if pref == 'dark':
            return 'dark'
        if pref == 'auto':
            return 'dark' if os_prefers_dark else 'light'
        if pref == 'schedule':
            if now_hour is None:
                return 'light'
            active = _is_within_schedule(
                now_hour,
                self.dark_mode_schedule_start,
                self.dark_mode_schedule_end,
            )
            return 'dark' if active else 'light'
        return 'light'

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        # Apply admin-scoped default policy to users that didn't explicitly
        # set a dark-mode preference at creation time. This is the only
        # integration point for `ld.dark_mode.config`.
        Config = self.env['ld.dark_mode.config'].sudo()
        for user, vals in zip(users, vals_list):
            if 'dark_mode_preference' in vals:
                continue
            policy = Config._get_default_for_user(user)
            if policy and policy.default_mode:
                user.sudo().write({
                    'dark_mode_preference': policy.default_mode,
                })
        return users

    @api.constrains('dark_mode_schedule_start', 'dark_mode_schedule_end')
    def _check_schedule_range(self):
        for user in self:
            for hour in (user.dark_mode_schedule_start, user.dark_mode_schedule_end):
                if hour < 0.0 or hour >= 24.0:
                    raise ValidationError(
                        'Dark Mode schedule hours must be within [0.0, 24.0).'
                    )
