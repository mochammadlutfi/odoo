from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models.phone_normalizer import PhoneNormalizer


class WhatsappSendWizard(models.TransientModel):
    _name = "whatsapp.send.wizard"
    _description = "WhatsApp Send Wizard"

    partner_id = fields.Many2one("res.partner", required=True)
    phone = fields.Char(required=True)
    phone_normalized = fields.Char(compute="_compute_phone_normalized", store=False)
    phone_valid = fields.Boolean(compute="_compute_phone_normalized", store=False)

    template_id = fields.Many2one(
        "whatsapp.template",
        domain="['|', ('model', '=', False), ('model', '=', related_model)]",
    )
    message = fields.Text()

    related_model = fields.Char(readonly=True)
    related_id = fields.Integer(readonly=True)

    @api.depends("phone")
    def _compute_phone_normalized(self):
        for wiz in self:
            normalized = PhoneNormalizer.normalize(wiz.phone)
            wiz.phone_normalized = normalized or ""
            wiz.phone_valid = bool(normalized)

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        # Auto-select default template for the related model + render it
        related_model = vals.get("related_model") or self.env.context.get(
            "default_related_model"
        )
        related_id = vals.get("related_id") or self.env.context.get("default_related_id")
        if related_model and related_id:
            tpl = self.env["whatsapp.template"].search(
                [
                    ("is_default", "=", True),
                    "|",
                    ("model", "=", related_model),
                    ("model", "=", False),
                ],
                limit=1,
            )
            if tpl:
                vals.setdefault("template_id", tpl.id)
                record = self.env[related_model].browse(related_id)
                vals.setdefault("message", tpl.render_for_record(record))
        return vals

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if not self.template_id:
            return
        record = None
        if self.related_model and self.related_id:
            record = self.env[self.related_model].browse(self.related_id).exists()
        if not record:
            record = self.partner_id
        if record:
            self.message = self.template_id.render_for_record(record)
        else:
            self.message = self.template_id.body

    def action_open_whatsapp(self):
        self.ensure_one()
        if not self.phone_valid:
            raise UserError(_("Phone number is not valid."))
        url = PhoneNormalizer.to_wa_url(self.phone, self.message or "")
        if not url:
            raise UserError(_("Cannot build WhatsApp URL from phone: %s") % self.phone)

        self._log_to_chatter()
        self._create_log()

        return {"type": "ir.actions.act_url", "url": url, "target": "new"}

    def _log_to_chatter(self):
        if not (self.related_model and self.related_id):
            return
        record = self.env[self.related_model].browse(self.related_id).exists()
        if not record or not hasattr(record, "message_post"):
            return
        tpl_name = self.template_id.name if self.template_id else _("Custom")
        body = _(
            "WhatsApp sent to %(name)s (%(phone)s)<br/>"
            "<i>Template: %(tpl)s</i><br/>"
            "<pre>%(msg)s</pre>"
        ) % {
            "name": self.partner_id.name or "",
            "phone": self.phone_normalized or "",
            "tpl": tpl_name,
            "msg": self.message or "",
        }
        record.message_post(body=body, message_type="comment")

    def _create_log(self):
        self.env["whatsapp.message.log"].create(
            {
                "partner_id": self.partner_id.id,
                "user_id": self.env.user.id,
                "template_id": self.template_id.id if self.template_id else False,
                "message_body": self.message,
                "phone_sent": self.phone_normalized,
                "related_model": self.related_model or False,
                "related_id": self.related_id or 0,
            }
        )
