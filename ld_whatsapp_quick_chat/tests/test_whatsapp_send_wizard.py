from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWhatsappSendWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {"name": "Ibu Ani", "mobile": "0812-3456-7890"}
        )

    def _create_wizard(self, **kwargs):
        vals = {
            "partner_id": self.partner.id,
            "phone": self.partner.mobile,
            "message": "Halo Ibu Ani",
            "related_model": "res.partner",
            "related_id": self.partner.id,
        }
        vals.update(kwargs)
        return self.env["whatsapp.send.wizard"].create(vals)

    def test_phone_normalized_computed(self):
        wiz = self._create_wizard()
        self.assertTrue(wiz.phone_valid)
        self.assertEqual(wiz.phone_normalized, "6281234567890")

    def test_invalid_phone_not_valid(self):
        wiz = self._create_wizard(phone="123")
        self.assertFalse(wiz.phone_valid)
        with self.assertRaises(UserError):
            wiz.action_open_whatsapp()

    def test_open_whatsapp_returns_act_url(self):
        wiz = self._create_wizard()
        action = wiz.action_open_whatsapp()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn("wa.me/6281234567890", action["url"])
        self.assertEqual(action["target"], "new")

    def test_open_whatsapp_creates_log(self):
        wiz = self._create_wizard()
        before = self.env["whatsapp.message.log"].search_count(
            [("partner_id", "=", self.partner.id)]
        )
        wiz.action_open_whatsapp()
        after = self.env["whatsapp.message.log"].search_count(
            [("partner_id", "=", self.partner.id)]
        )
        self.assertEqual(after, before + 1)

    def test_open_whatsapp_logs_to_chatter(self):
        """The related record should get a chatter message."""
        wiz = self._create_wizard()
        wiz.action_open_whatsapp()
        messages = self.partner.message_ids.filtered(
            lambda m: "WhatsApp sent" in (m.body or "")
        )
        self.assertTrue(messages)

    def test_template_auto_render_via_onchange(self):
        tpl = self.env["whatsapp.template"].create(
            {"name": "T1", "body": "Halo {{partner_name}}!"}
        )
        wiz = self._create_wizard()
        wiz.template_id = tpl
        wiz._onchange_template_id()
        self.assertEqual(wiz.message, "Halo Ibu Ani!")
