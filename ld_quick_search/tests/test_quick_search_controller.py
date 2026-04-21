from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestQuickSearchController(HttpCase):

    def test_search_menus_json(self):
        self.authenticate('admin', 'admin')
        resp = self.url_open(
            '/ld_quick_search/search',
            data='{"jsonrpc":"2.0","params":{"query":"settings","scope":"menu"}}',
            headers={'Content-Type': 'application/json'},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('result', data)
        results = data['result'].get('results', [])
        self.assertIsInstance(results, list)

    def test_search_records_respects_acl(self):
        portal_user = self.env['res.users'].create({
            'name': 'Portal QS',
            'login': 'portal_qs',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
        })
        self.authenticate('portal_qs', 'portal_qs')
        resp = self.url_open(
            '/ld_quick_search/search',
            data='{"jsonrpc":"2.0","params":{"query":"partner","scope":"record","model":"res.partner"}}',
            headers={'Content-Type': 'application/json'},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        results = (data.get('result') or {}).get('results', [])
        self.assertIsInstance(results, list, 'must not 500 on ACL-denied models')

    def test_search_unknown_scope_rejected(self):
        self.authenticate('admin', 'admin')
        resp = self.url_open(
            '/ld_quick_search/search',
            data='{"jsonrpc":"2.0","params":{"query":"x","scope":"__evil__"}}',
            headers={'Content-Type': 'application/json'},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('error', data, 'unknown scope must error cleanly, not crash')
