from odoo import _, fields, models
from odoo.exceptions import UserError

from .phone_normalizer import PhoneNormalizer


class ResPartner(models.Model):
    _inherit = "res.partner"

    whatsapp_valid = fields.Boolean(
        compute="_compute_whatsapp_valid",
        help="True when the partner has a valid phone/mobile for WhatsApp.",
    )

    def _compute_whatsapp_valid(self):
        for partner in self:
            partner.whatsapp_valid = PhoneNormalizer.is_valid(
                partner.mobile or partner.phone
            )

    def _wa_phone(self):
        """Return best phone for WA (mobile preferred)."""
        self.ensure_one()
        return self.mobile or self.phone or ""

    def action_send_whatsapp(self):
        """Open the WhatsApp send wizard for this partner."""
        self.ensure_one()
        phone = self._wa_phone()
        if not PhoneNormalizer.is_valid(phone):
            raise UserError(
                _("Phone number is empty or invalid for WhatsApp. "
                  "Expected format: +62 812..., 0812..., or 812...")
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Send WhatsApp"),
            "res_model": "whatsapp.send.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.id,
                "default_phone": phone,
                "default_related_model": self._name,
                "default_related_id": self.id,
            },
        }

    def action_bulk_send_whatsapp(self):
        """List-view bulk action -> open the bulk wizard."""
        partners = self.filtered(lambda p: PhoneNormalizer.is_valid(p.mobile or p.phone))
        if not partners:
            raise UserError(_("No selected partner has a valid WhatsApp phone number."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Send WhatsApp Broadcast"),
            "res_model": "whatsapp.bulk.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_ids": [(6, 0, partners.ids)],
                "default_related_model": self._name,
            },
        }
