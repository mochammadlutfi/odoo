from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        ICP = self.env['ir.config_parameter'].sudo()
        result['ld_quick_search_shortcut'] = ICP.get_param(
            'ld_quick_search.shortcut', default='ctrl+k',
        )
        return result
