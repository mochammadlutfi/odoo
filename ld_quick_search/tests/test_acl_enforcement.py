from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAclEnforcement(TransactionCase):
    """Ensures record search never returns records the user cannot read."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = cls.env['res.users'].create({
            'name': 'Portal Tester',
            'login': 'portal_tester',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })

    def test_blacklist_model_returns_empty(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'ld_quick_search.blacklist_models',
            'res.users,res.groups',
        )
        Search = self.env['ld.quick_search.engine']
        results = Search.with_user(self.portal_user).search_records(
            model='res.users', query='admin',
        )
        self.assertEqual(results, [], 'blacklisted model must return empty')

    def test_unknown_model_returns_empty(self):
        Search = self.env['ld.quick_search.engine']
        results = Search.with_user(self.portal_user).search_records(
            model='does.not.exist', query='anything',
        )
        self.assertEqual(results, [])

    def test_portal_cannot_search_privileged_model(self):
        Search = self.env['ld.quick_search.engine']
        # Must not raise — must fail closed with empty list
        try:
            results = Search.with_user(self.portal_user).search_records(
                model='res.users', query='admin',
            )
        except AccessError:
            self.fail('search_records must fail closed, not raise AccessError to caller')
        self.assertEqual(results, [])
