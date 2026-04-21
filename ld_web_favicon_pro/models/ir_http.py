import time

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        ctx = super().webclient_rendering_context()
        company = request.env.company
        if company.favicon:
            ts = int(time.time() // 3600)
            ctx['x_icon'] = f'/ld_favicon/favicon.ico?v={ts}'
        return ctx
