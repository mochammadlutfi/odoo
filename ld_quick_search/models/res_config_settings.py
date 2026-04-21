from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quick_search_shortcut = fields.Char(
        string='Quick Search Shortcut',
        default='ctrl+k',
        config_parameter='ld_quick_search.shortcut',
        help="Keyboard shortcut to open the quick search palette. "
             "Use 'ctrl+k' (auto-maps to Cmd+K on Mac).",
    )
    quick_search_blacklist_models = fields.Char(
        string='Blacklist Models',
        default='',
        config_parameter='ld_quick_search.blacklist_models',
        help='Comma-separated list of models excluded from record search '
             '(e.g. "res.users,account.journal").',
    )
    quick_search_whitelist_models = fields.Char(
        string='Whitelist Models (optional)',
        default='',
        config_parameter='ld_quick_search.whitelist_models',
        help='If set, only these models are searchable. Leave empty to allow all '
             '(minus blacklist).',
    )
    quick_search_record_limit = fields.Integer(
        string='Record Result Limit',
        default=10,
        config_parameter='ld_quick_search.record_limit',
    )
