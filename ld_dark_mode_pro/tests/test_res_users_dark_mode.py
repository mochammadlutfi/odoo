from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestResUsersDarkMode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Dark Mode Test User',
            'login': 'ld_dm_test_user',
        })

    def test_default_preference_is_auto(self):
        self.assertEqual(self.user.dark_mode_preference, 'auto')

    def test_default_schedule_values(self):
        self.assertEqual(self.user.dark_mode_schedule_start, 19.0)
        self.assertEqual(self.user.dark_mode_schedule_end, 7.0)

    def test_self_writeable_fields_exposed(self):
        fields_set = set(self.user.SELF_WRITEABLE_FIELDS)
        self.assertIn('dark_mode_preference', fields_set)
        self.assertIn('dark_mode_schedule_start', fields_set)
        self.assertIn('dark_mode_schedule_end', fields_set)

    def test_self_readable_fields_exposed(self):
        fields_set = set(self.user.SELF_READABLE_FIELDS)
        self.assertIn('dark_mode_preference', fields_set)
        self.assertIn('dark_mode_schedule_start', fields_set)
        self.assertIn('dark_mode_schedule_end', fields_set)

    def test_compute_effective_light_preference(self):
        self.user.dark_mode_preference = 'light'
        self.assertEqual(
            self.user._resolve_effective_dark_mode(now_hour=22.0),
            'light',
        )

    def test_compute_effective_dark_preference(self):
        self.user.dark_mode_preference = 'dark'
        self.assertEqual(
            self.user._resolve_effective_dark_mode(now_hour=10.0),
            'dark',
        )

    def test_compute_effective_auto_follows_os(self):
        self.user.dark_mode_preference = 'auto'
        self.assertEqual(
            self.user._resolve_effective_dark_mode(os_prefers_dark=True),
            'dark',
        )
        self.assertEqual(
            self.user._resolve_effective_dark_mode(os_prefers_dark=False),
            'light',
        )

    def test_compute_effective_schedule_evening(self):
        self.user.write({
            'dark_mode_preference': 'schedule',
            'dark_mode_schedule_start': 19.0,
            'dark_mode_schedule_end': 7.0,
        })
        self.assertEqual(
            self.user._resolve_effective_dark_mode(now_hour=22.5),
            'dark',
        )
        self.assertEqual(
            self.user._resolve_effective_dark_mode(now_hour=12.0),
            'light',
        )

    def test_compute_effective_schedule_without_time_defaults_light(self):
        self.user.dark_mode_preference = 'schedule'
        self.assertEqual(self.user._resolve_effective_dark_mode(), 'light')

    def test_schedule_constraint_rejects_out_of_range(self):
        with self.assertRaises(ValidationError):
            self.user.write({'dark_mode_schedule_start': 24.0})
        with self.assertRaises(ValidationError):
            self.user.write({'dark_mode_schedule_end': -1.0})

    def test_user_can_self_write_preference(self):
        """A non-admin user must be able to set their own dark_mode_preference
        via the self-service API (covers the RPC used by the OWL toggle)."""
        user_self = self.user.with_user(self.user)
        user_self.write({'dark_mode_preference': 'dark'})
        self.assertEqual(self.user.dark_mode_preference, 'dark')
