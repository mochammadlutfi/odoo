"""WhatsApp message template.

Rendering uses a simple, explicit placeholder map — NOT Odoo's mail.render.mixin.
Reason: mail.render.mixin restricts non-admin users to a ~7-expression allowlist
(object.name, object.partner_id.name, etc.) and raises AccessError for anything
else. Sales/CS users need to render templates daily, so we use a hand-rolled
substitution for safety + simplicity.

Supported placeholders (double curly braces):
    {{partner_name}}     -> record.partner_id.name or record.name
    {{partner_phone}}    -> partner's mobile or phone
    {{record_name}}      -> record.name (SO00123, INV/2026/001, ...)
    {{amount}}           -> record.amount_total, IDR-formatted as "1,500,000"
    {{amount_raw}}       -> record.amount_total, raw number
    {{invoice_number}}   -> record.name (alias for account.move)
    {{due_date}}         -> record.invoice_date_due formatted "%d %B %Y"
    {{company_name}}     -> env.company.name
    {{user_name}}        -> env.user.name
    {{user_signature}}   -> env.user.signature (stripped of HTML tags)
"""
import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

WA_MAX_CHARS = 4096
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-z_][a-z0-9_]*)\s*\}\}", re.IGNORECASE)


class WhatsappTemplate(models.Model):
    _name = "whatsapp.template"
    _description = "WhatsApp Message Template"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    model_id = fields.Many2one(
        "ir.model",
        string="Applicable Model",
        ondelete="cascade",
        help="Restrict this template to records of this model. Empty = available everywhere.",
    )
    model = fields.Char(
        related="model_id.model",
        store=True,
        readonly=True,
        string="Model Name",
    )
    body = fields.Text(
        required=True,
        translate=True,
        help="Message body. Use placeholders like {{partner_name}}, "
             "{{record_name}}, {{amount}}, {{invoice_number}}, "
             "{{due_date}}, {{company_name}}, {{user_name}}.",
    )
    active = fields.Boolean(default=True)
    is_default = fields.Boolean(
        string="Default",
        help="If set, auto-selected when opening the Send wizard for its model.",
    )
    category = fields.Selection(
        [
            ("order", "Order"),
            ("invoice", "Invoice"),
            ("follow_up", "Follow-up"),
            ("greeting", "Greeting"),
            ("reminder", "Reminder"),
            ("thank_you", "Thank You"),
            ("complaint", "Complaint"),
            ("general", "General"),
        ],
        default="general",
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Allowed Users",
        help="Users who can use this template. Empty = all users.",
    )

    @api.constrains("body")
    def _check_body_length(self):
        for tpl in self:
            if tpl.body and len(tpl.body) > WA_MAX_CHARS:
                raise ValidationError(
                    _("Template body exceeds WhatsApp limit (%d chars).") % WA_MAX_CHARS
                )

    # -- rendering -----------------------------------------------------

    def _build_context(self, record):
        """Build the placeholder -> value map for `record`.

        `record` may be any recordset with one record, partner or otherwise.
        Missing fields resolve to empty string so templates stay robust.
        """
        env = self.env
        ctx = {
            "company_name": env.company.name or "",
            "user_name": env.user.name or "",
            "user_signature": self._strip_html(env.user.signature or ""),
        }
        if not record:
            return ctx

        # Partner resolution:
        # - res.partner record -> use itself (its own partner_id is the commercial parent)
        # - other models with partner_id -> use that partner
        if record._name == "res.partner":
            partner = record
        elif "partner_id" in record._fields:
            partner = record.partner_id
        else:
            partner = record.browse()  # empty recordset
        if partner:
            ctx["partner_name"] = partner.name or ""
            ctx["partner_phone"] = partner.mobile or partner.phone or ""
        else:
            ctx["partner_name"] = record.name if "name" in record._fields else ""
            ctx["partner_phone"] = ""

        # Record name (only for non-partner records; partner name already covered)
        if "name" in record._fields:
            ctx["record_name"] = record.name or ""
            if record._name != "res.partner":
                ctx["invoice_number"] = record.name or ""

        # Amounts — check field existence explicitly (don't short-circuit on 0)
        if "amount_total" in record._fields:
            amount = record.amount_total or 0.0
            ctx["amount"] = f"{amount:,.0f}"
            ctx["amount_raw"] = str(amount)

        # Due date (for invoices)
        if "invoice_date_due" in record._fields and record.invoice_date_due:
            try:
                ctx["due_date"] = record.invoice_date_due.strftime("%d %B %Y")
            except Exception:  # pragma: no cover
                ctx["due_date"] = str(record.invoice_date_due)

        return ctx

    @staticmethod
    def _strip_html(value):
        return re.sub(r"<[^>]+>", "", value or "").strip()

    def render_for_record(self, record):
        """Render the template body for a single record."""
        self.ensure_one()
        if not self.body:
            return ""
        ctx = self._build_context(record)

        def _sub(match):
            key = match.group(1).lower()
            return str(ctx.get(key, match.group(0)))

        return _PLACEHOLDER_RE.sub(_sub, self.body)
