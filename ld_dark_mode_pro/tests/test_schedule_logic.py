from odoo.tests.common import BaseCase

from odoo.addons.ld_dark_mode_pro.models.res_users import _is_within_schedule


class TestScheduleLogic(BaseCase):
    """Pure function tests — no DB required."""

    def test_daytime_window_hit(self):
        self.assertTrue(_is_within_schedule(10.0, 9.0, 17.0))

    def test_daytime_window_miss_before(self):
        self.assertFalse(_is_within_schedule(8.0, 9.0, 17.0))

    def test_daytime_window_miss_after(self):
        self.assertFalse(_is_within_schedule(17.0, 9.0, 17.0),
                         "end is exclusive")

    def test_daytime_window_hit_at_start(self):
        self.assertTrue(_is_within_schedule(9.0, 9.0, 17.0),
                        "start is inclusive")

    def test_wraparound_hit_late_night(self):
        self.assertTrue(_is_within_schedule(22.5, 19.0, 7.0))

    def test_wraparound_hit_early_morning(self):
        self.assertTrue(_is_within_schedule(2.0, 19.0, 7.0))

    def test_wraparound_miss_midday(self):
        self.assertFalse(_is_within_schedule(12.0, 19.0, 7.0))

    def test_wraparound_boundary_start_inclusive(self):
        self.assertTrue(_is_within_schedule(19.0, 19.0, 7.0))

    def test_wraparound_boundary_end_exclusive(self):
        self.assertFalse(_is_within_schedule(7.0, 19.0, 7.0))

    def test_zero_window_never_active(self):
        self.assertFalse(_is_within_schedule(12.0, 8.0, 8.0))
        self.assertFalse(_is_within_schedule(8.0, 8.0, 8.0))

    def test_fractional_hours(self):
        self.assertTrue(_is_within_schedule(19.5, 19.25, 19.75))
        self.assertFalse(_is_within_schedule(19.8, 19.25, 19.75))
