import json

from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install', '-standard')
class TestDarkModeController(HttpCase):
    def setUp(self):
        super().setUp()
        self.user_password = 'ld_dm_ctrl_pw'
        self.user = self.env['res.users'].create({
            'name': 'Ctrl Test User',
            'login': 'ld_dm_ctrl',
            'password': self.user_password,
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

    def _rpc(self, url, payload):
        return self.url_open(
            url,
            data=json.dumps({'params': payload}),
            headers={'Content-Type': 'application/json'},
        )

    def test_set_dark_mode_sets_cookie(self):
        self.authenticate('ld_dm_ctrl', self.user_password)
        response = self._rpc('/ld_dark_mode/set', {'mode': 'dark'})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body.get('result', {}).get('mode'), 'dark')
        set_cookie = response.headers.get('Set-Cookie', '')
        self.assertIn('color_scheme=dark', set_cookie)

    def test_set_light_mode_sets_cookie(self):
        self.authenticate('ld_dm_ctrl', self.user_password)
        response = self._rpc('/ld_dark_mode/set', {'mode': 'light'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('color_scheme=light',
                      response.headers.get('Set-Cookie', ''))

    def test_invalid_mode_returns_error(self):
        self.authenticate('ld_dm_ctrl', self.user_password)
        response = self._rpc('/ld_dark_mode/set', {'mode': 'rainbow'})
        body = response.json()
        self.assertIn('error', body, "invalid mode should surface a JSON-RPC error")

    def test_unauthenticated_call_denied(self):
        response = self._rpc('/ld_dark_mode/set', {'mode': 'dark'})
        body = response.json()
        self.assertIn('error', body)

    def test_clear_cookie(self):
        self.authenticate('ld_dm_ctrl', self.user_password)
        response = self._rpc('/ld_dark_mode/clear', {})
        self.assertEqual(response.status_code, 200)
        set_cookie = response.headers.get('Set-Cookie', '')
        self.assertIn('color_scheme=', set_cookie)
        # max-age=0 is what actually clears the cookie on the client
        self.assertIn('Max-Age=0', set_cookie)
