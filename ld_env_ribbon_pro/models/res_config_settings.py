import os
from odoo import api, fields, models

ENVIRONMENT_COLORS = {
    'dev': '#3b82f6',
    'staging': '#f59e0b',
    'uat': '#a855f7',
    'production': '#ef4444',
    'demo': '#6b7280',
    'test': '#10b981',
}

ENVIRONMENT_TEXT = {
    'dev': 'DEVELOPMENT',
    'staging': 'STAGING',
    'uat': 'UAT',
    'production': 'PRODUCTION',
    'demo': 'DEMO',
    'test': 'TEST',
}

ENV_VAR_MAPPING = {
    'dev': 'dev', 'development': 'dev',
    'stg': 'staging', 'staging': 'staging',
    'uat': 'uat',
    'prod': 'production', 'production': 'production',
    'demo': 'demo',
    'test': 'test',
}


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ribbon_enabled = fields.Boolean(
        string='Enable Environment Ribbon',
        config_parameter='ld_env_ribbon_pro.ribbon_enabled',
    )
    ribbon_environment = fields.Selection(
        selection=[
            ('dev', 'Development'),
            ('staging', 'Staging'),
            ('uat', 'UAT'),
            ('production', 'Production'),
            ('demo', 'Demo'),
            ('test', 'Test'),
            ('custom', 'Custom'),
        ],
        string='Environment Type',
        config_parameter='ld_env_ribbon_pro.ribbon_environment',
    )
    ribbon_text_custom = fields.Char(
        string='Custom Text',
        config_parameter='ld_env_ribbon_pro.ribbon_text_custom',
    )
    ribbon_style = fields.Selection(
        selection=[
            ('bar', 'Bar (Straight)'),
            ('corner', 'Corner (Diagonal)'),
            ('vertical', 'Vertical (Sideways)'),
            ('banner', 'Banner (Full Width)'),
        ],
        string='Ribbon Style',
        config_parameter='ld_env_ribbon_pro.ribbon_style',
        default='bar',
    )
    ribbon_position = fields.Selection(
        selection=[
            ('top_right', 'Top Right'),
            ('top_left', 'Top Left'),
            ('bottom_right', 'Bottom Right'),
            ('bottom_left', 'Bottom Left'),
        ],
        string='Position',
        config_parameter='ld_env_ribbon_pro.ribbon_position',
        default='top_right',
    )
    ribbon_color_mode = fields.Selection(
        selection=[
            ('preset', 'Use Preset Color'),
            ('custom', 'Custom Color'),
        ],
        string='Color Mode',
        config_parameter='ld_env_ribbon_pro.ribbon_color_mode',
        default='preset',
    )
    ribbon_color_custom = fields.Char(
        string='Custom Color (Hex)',
        config_parameter='ld_env_ribbon_pro.ribbon_color_custom',
    )
    ribbon_user_dismissable = fields.Boolean(
        string='Allow users to dismiss ribbon',
        config_parameter='ld_env_ribbon_pro.ribbon_user_dismissable',
    )
    ribbon_audit_production_access = fields.Boolean(
        string='Audit Production Access',
        config_parameter='ld_env_ribbon_pro.ribbon_audit_production_access',
    )
    ribbon_env_var_detected = fields.Char(
        string='Detected ODOO_ENV',
        compute='_compute_ribbon_env_var_detected',
    )

    @api.depends()
    def _compute_ribbon_env_var_detected(self):
        env_var = os.environ.get('ODOO_ENV', '')
        detected = ENV_VAR_MAPPING.get(env_var.lower(), '')
        for rec in self:
            rec.ribbon_env_var_detected = detected or env_var or 'Not set'

    def get_ribbon_config(self):
        """Return ribbon config dict for session_info injection."""
        ICP = self.env['ir.config_parameter'].sudo()

        enabled_raw = ICP.get_param('ld_env_ribbon_pro.ribbon_enabled', 'False')
        enabled = enabled_raw in ('True', '1', 'true')

        # ODOO_ENV variable overrides manual setting
        env_var = os.environ.get('ODOO_ENV', '').lower()
        env_override = ENV_VAR_MAPPING.get(env_var)

        environment = env_override or ICP.get_param('ld_env_ribbon_pro.ribbon_environment', '')
        color_mode = ICP.get_param('ld_env_ribbon_pro.ribbon_color_mode', 'preset')
        color_custom = ICP.get_param('ld_env_ribbon_pro.ribbon_color_custom', '')

        if color_mode == 'custom' and color_custom:
            color = color_custom
        else:
            color = ENVIRONMENT_COLORS.get(environment, '#6b7280')

        text_custom = ICP.get_param('ld_env_ribbon_pro.ribbon_text_custom', '')
        text = text_custom or ENVIRONMENT_TEXT.get(environment, environment.upper() if environment else '')

        dismissable_raw = ICP.get_param('ld_env_ribbon_pro.ribbon_user_dismissable', 'True')
        dismissable = dismissable_raw in ('True', '1', 'true')

        # Force non-dismissable for production
        if environment == 'production':
            dismissable = False

        return {
            'enabled': enabled,
            'environment': environment,
            'text': text,
            'color': color,
            'style': ICP.get_param('ld_env_ribbon_pro.ribbon_style', 'bar'),
            'position': ICP.get_param('ld_env_ribbon_pro.ribbon_position', 'top_right'),
            'user_dismissable': dismissable,
            'env_var_override': bool(env_override),
        }
