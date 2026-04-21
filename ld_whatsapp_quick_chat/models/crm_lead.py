from odoo import _, models
from odoo.exceptions import UserError

from .phone_normalizer import PhoneNormalizer


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_send_whatsapp(self):
        self.ensure_one()
        phone = self.mobile or self.phone or (
            self.partner_id.mobile or self.partner_id.phone if self.partner_id else ""
        )
        if not PhoneNormalizer.is_valid(phone):
            raise UserError(_("No valid WhatsApp phone on this lead or its partner."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Send WhatsApp"),
            "res_model": "whatsapp.send.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.partner_id.id if self.partner_id else False,
                "default_phone": phone,
                "default_related_model": self._name,
                "default_related_id": self.id,
            },
        }
