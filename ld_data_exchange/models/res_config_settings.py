from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    copy_field_double_click = fields.Boolean(
        string='Enable Double-Click Copy',
        config_parameter='ld_data_exchange.copy_field_double_click',
        default=True,
    )
    default_copy_format = fields.Selection([
        ('tsv', 'TSV (Excel-compatible)'),
        ('csv', 'CSV'),
        ('markdown', 'Markdown Table'),
        ('json', 'JSON'),
    ], string='Default Copy Format',
       config_parameter='ld_data_exchange.default_format',
       default='tsv',
    )
