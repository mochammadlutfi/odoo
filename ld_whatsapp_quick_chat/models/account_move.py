from odoo import _, models
from odoo.exceptions import UserError

from .phone_normalizer import PhoneNormalizer


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_send_whatsapp(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("This document has no partner."))
        phone = self.partner_id.mobile or self.partner_id.phone
        if not PhoneNormalizer.is_valid(phone):
            raise UserError(_("Partner has no valid WhatsApp phone number."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Send WhatsApp"),
            "res_model": "whatsapp.send.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_phone": phone,
                "default_related_model": self._name,
                "default_related_id": self.id,
            },
        }
