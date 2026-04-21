from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPartnerAction(TransactionCase):
    def test_partner_action_returns_wizard(self):
        partner = self.env["res.partner"].create(
            {"name": "Test", "mobile": "08123456789"}
        )
        action = partner.action_send_whatsapp()
        self.assertEqual(action["res_model"], "whatsapp.send.wizard")
        self.assertEqual(action["context"]["default_partner_id"], partner.id)

    def test_partner_invalid_phone_raises(self):
        partner = self.env["res.partner"].create(
            {"name": "NoPhone", "mobile": False, "phone": False}
        )
        with self.assertRaises(UserError):
            partner.action_send_whatsapp()

    def test_partner_whatsapp_valid_computed(self):
        partner_ok = self.env["res.partner"].create(
            {"name": "OK", "mobile": "08123456789"}
        )
        partner_bad = self.env["res.partner"].create(
            {"name": "Bad", "mobile": "abc"}
        )
        self.assertTrue(partner_ok.whatsapp_valid)
        self.assertFalse(partner_bad.whatsapp_valid)

    def test_bulk_send_no_valid_partners(self):
        partner = self.env["res.partner"].create(
            {"name": "Bad", "mobile": False, "phone": False}
        )
        with self.assertRaises(UserError):
            partner.action_bulk_send_whatsapp()

    def test_bulk_send_returns_wizard_action(self):
        partners = self.env["res.partner"].create(
            [
                {"name": "A", "mobile": "08123456789"},
                {"name": "B", "mobile": "0812-3456-7891"},
            ]
        )
        action = partners.action_bulk_send_whatsapp()
        self.assertEqual(action["res_model"], "whatsapp.bulk.wizard")
        self.assertIn(partners[0].id, action["context"]["default_partner_ids"][0][2])
