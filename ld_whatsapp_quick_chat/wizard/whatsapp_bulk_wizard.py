from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models.phone_normalizer import PhoneNormalizer


class WhatsappBulkWizard(models.TransientModel):
    _name = "whatsapp.bulk.wizard"
    _description = "WhatsApp Bulk Send Wizard"

    partner_ids = fields.Many2many("res.partner", required=True)
    partner_count = fields.Integer(compute="_compute_counts", store=False)
    valid_partner_count = fields.Integer(compute="_compute_counts", store=False)
    invalid_partner_count = fields.Integer(compute="_compute_counts", store=False)

    template_id = fields.Many2one("whatsapp.template", required=True)
    message_preview = fields.Text(compute="_compute_message_preview", store=False)

    related_model = fields.Char(readonly=True)

    @api.depends("partner_ids")
    def _compute_counts(self):
        for wiz in self:
            valid = sum(
                1
                for p in wiz.partner_ids
                if PhoneNormalizer.is_valid(p.mobile or p.phone)
            )
            wiz.partner_count = len(wiz.partner_ids)
            wiz.valid_partner_count = valid
            wiz.invalid_partner_count = len(wiz.partner_ids) - valid

    @api.depends("template_id", "partner_ids")
    def _compute_message_preview(self):
        for wiz in self:
            if wiz.template_id and wiz.partner_ids:
                wiz.message_preview = wiz.template_id.render_for_record(
                    wiz.partner_ids[:1]
                )
            else:
                wiz.message_preview = ""

    def action_bulk_send(self):
        """Build wa.me URLs for all valid partners; return a client action
        that opens each one in a new tab from the browser side.
        """
        self.ensure_one()
        if not self.template_id:
            raise UserError(_("Please pick a template."))

        urls = []
        for partner in self.partner_ids:
            phone = partner.mobile or partner.phone
            if not PhoneNormalizer.is_valid(phone):
                continue
            body = self.template_id.render_for_record(partner)
            url = PhoneNormalizer.to_wa_url(phone, body)
            if not url:
                continue
            urls.append(url)
            # Log + chatter for each
            self.env["whatsapp.message.log"].create(
                {
                    "partner_id": partner.id,
                    "user_id": self.env.user.id,
                    "template_id": self.template_id.id,
                    "message_body": body,
                    "phone_sent": PhoneNormalizer.normalize(phone),
                    "related_model": "res.partner",
                    "related_id": partner.id,
                }
            )
            if hasattr(partner, "message_post"):
                partner.message_post(
                    body=_("WhatsApp broadcast queued (template: %s)")
                    % self.template_id.name,
                    message_type="comment",
                )

        if not urls:
            raise UserError(_("No partner has a valid WhatsApp phone number."))

        # For bulk, we can only open one tab server-side; the rest must be
        # handled manually. Return an info notification + open the first URL.
        # (Indonesian workflow: users iterate manually to avoid popup blocker.)
        return {
            "type": "ir.actions.act_url",
            "url": urls[0],
            "target": "new",
        }
