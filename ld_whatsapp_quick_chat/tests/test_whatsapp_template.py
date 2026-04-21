from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWhatsappTemplate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {"name": "Bapak Budi", "mobile": "08123456789"}
        )

    def test_render_partner_name(self):
        tpl = self.env["whatsapp.template"].create(
            {"name": "Hello", "body": "Halo {{partner_name}}!"}
        )
        self.assertEqual(tpl.render_for_record(self.partner), "Halo Bapak Budi!")

    def test_render_company_name(self):
        tpl = self.env["whatsapp.template"].create(
            {"name": "Company", "body": "From {{company_name}}"}
        )
        rendered = tpl.render_for_record(self.partner)
        self.assertIn(self.env.company.name, rendered)

    def test_render_with_sale_order_like_record(self):
        """Template should render amount/record_name on records that expose those fields."""
        tpl = self.env["whatsapp.template"].create(
            {
                "name": "Order",
                "body": "Order {{record_name}} total Rp {{amount}}",
            }
        )
        partner = self.env["res.partner"].create({"name": "Ibu Ani"})
        # A draft move's `name` is "/", posted moves get "INV/…" — either is a string.
        move = self.env["account.move"].create(
            {"partner_id": partner.id, "move_type": "out_invoice"}
        )
        rendered = tpl.render_for_record(move)
        # record_name should appear (move.name is "/" for drafts — still a str).
        self.assertIn(str(move.name or ""), rendered)
        self.assertIn("Rp ", rendered)
        self.assertNotIn("{{amount}}", rendered)

    def test_unknown_placeholder_preserved(self):
        """Unknown {{foo}} stays as-is so user sees the typo."""
        tpl = self.env["whatsapp.template"].create(
            {"name": "Typo", "body": "X {{totally_unknown}} Y"}
        )
        rendered = tpl.render_for_record(self.partner)
        self.assertEqual(rendered, "X {{totally_unknown}} Y")

    def test_body_length_validation(self):
        with self.assertRaises(ValidationError):
            self.env["whatsapp.template"].create(
                {"name": "Too long", "body": "x" * 4097}
            )

    def test_body_at_limit_ok(self):
        tpl = self.env["whatsapp.template"].create(
            {"name": "At limit", "body": "x" * 4096}
        )
        self.assertTrue(tpl.id)

    def test_seed_templates_installed(self):
        """Default templates should ship with the module."""
        refs = [
            "ld_whatsapp_quick_chat.wa_template_order_confirm",
            "ld_whatsapp_quick_chat.wa_template_invoice_reminder",
            "ld_whatsapp_quick_chat.wa_template_follow_up",
        ]
        for ref in refs:
            tpl = self.env.ref(ref)
            self.assertTrue(tpl.id, f"{ref} not installed")

    def test_seed_order_template_renders(self):
        """The built-in SO template should render on a sale.order."""
        tpl = self.env.ref("ld_whatsapp_quick_chat.wa_template_order_confirm")
        product = self.env["product.product"].search([], limit=1)
        self.assertTrue(product, "demo DB should have at least one product")
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [(0, 0, {
                    "product_id": product.id,
                    "product_uom_qty": 1,
                })],
            }
        )
        rendered = tpl.render_for_record(order)
        self.assertIn("Bapak Budi", rendered)
        self.assertIn(order.name, rendered)
        self.assertNotIn("{{", rendered)
