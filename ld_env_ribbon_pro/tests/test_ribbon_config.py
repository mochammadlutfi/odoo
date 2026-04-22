from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRibbonConfig(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ICP = self.env['ir.config_parameter'].sudo()
        self.Settings = self.env['res.config.settings']

    def test_default_ribbon_disabled(self):
        """Ribbon should be disabled by default."""
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_enabled', 'False')
        cfg = self.Settings.get_ribbon_config()
        self.assertFalse(cfg['enabled'])

    def test_production_forces_non_dismissable(self):
        """Production environment must not be dismissable regardless of setting."""
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_enabled', 'True')
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_environment', 'production')
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_user_dismissable', 'True')
        cfg = self.Settings.get_ribbon_config()
        self.assertEqual(cfg['environment'], 'production')
        self.assertFalse(cfg['user_dismissable'])

    def test_preset_color_by_environment(self):
        """Preset color mode should return the environment-mapped color."""
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_enabled', 'True')
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_environment', 'dev')
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_color_mode', 'preset')
        cfg = self.Settings.get_ribbon_config()
        self.assertEqual(cfg['color'], '#3b82f6')

    def test_custom_color_override(self):
        """Custom color mode should override the preset."""
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_enabled', 'True')
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_environment', 'dev')
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_color_mode', 'custom')
        self.ICP.set_param('ld_env_ribbon_pro.ribbon_color_custom', '#123456')
        cfg = self.Settings.get_ribbon_config()
        self.assertEqual(cfg['color'], '#123456')
