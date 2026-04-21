from odoo import fields, models


class WhatsappMessageLog(models.Model):
    _name = "whatsapp.message.log"
    _description = "WhatsApp Message Log"
    _order = "send_time desc"

    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        required=True,
        ondelete="restrict",
    )
    template_id = fields.Many2one("whatsapp.template", ondelete="set null")
    message_body = fields.Text()
    phone_sent = fields.Char(string="Phone (normalized)")
    send_time = fields.Datetime(default=fields.Datetime.now, required=True)
    related_model = fields.Char(string="Related Model")
    related_id = fields.Integer(string="Related Record ID")
