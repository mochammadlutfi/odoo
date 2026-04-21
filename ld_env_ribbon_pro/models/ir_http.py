import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        info = super().session_info()
        try:
            ribbon_config = self.env['res.config.settings'].get_ribbon_config()
            info['ribbon_config'] = ribbon_config

            # Log production access if audit is enabled
            if ribbon_config.get('enabled') and ribbon_config.get('environment') == 'production':
                self._log_production_access(ribbon_config)
        except Exception:
            _logger.exception('Error injecting ribbon config into session_info')
            info['ribbon_config'] = {'enabled': False}
        return info

    def _log_production_access(self, ribbon_config):
        ICP = self.env['ir.config_parameter'].sudo()
        audit_raw = ICP.get_param('ld_env_ribbon_pro.ribbon_audit_production_access', 'True')
        if audit_raw not in ('True', '1', 'true'):
            return

        uid = self.env.uid
        if not uid or uid == self.env.ref('base.public_user').id:
            return

        ip = request.httprequest.remote_addr if request else None
        ua = request.httprequest.user_agent.string if request else None

        try:
            self.env['env.ribbon.audit.log'].sudo().create({
                'user_id': uid,
                'ip_address': ip,
                'user_agent': ua,
                'action_type': 'session',
            })
        except Exception:
            _logger.exception('Failed to create ribbon audit log entry')
