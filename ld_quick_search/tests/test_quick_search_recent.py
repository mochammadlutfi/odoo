from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestQuickSearchRecent(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'QS Tester',
            'login': 'qs_tester',
        })
        cls.Recent = cls.env['ld.quick_search.recent']

    def test_record_for_user_with_query(self):
        rec = self.Recent.with_user(self.user).record_usage(
            action_id=False,
            res_model='res.partner',
            res_id=False,
            query='partner john',
        )
        self.assertTrue(rec, 'record_usage should return a recorded entry')
        self.assertEqual(rec.user_id, self.user)
        self.assertEqual(rec.use_count, 1)
        self.assertEqual(rec.search_query, 'partner john')

    def test_increment_use_count_on_duplicate(self):
        first = self.Recent.with_user(self.user).record_usage(
            action_id=False,
            res_model='res.partner',
            res_id=False,
            query='acme',
        )
        second = self.Recent.with_user(self.user).record_usage(
            action_id=False,
            res_model='res.partner',
            res_id=False,
            query='acme',
        )
        self.assertEqual(first, second, 'duplicate usage should upsert same row')
        self.assertEqual(second.use_count, 2)

    def test_per_user_isolation(self):
        other = self.env['res.users'].create({
            'name': 'QS Other',
            'login': 'qs_other',
        })
        self.Recent.with_user(self.user).record_usage(
            action_id=False, res_model='res.partner', res_id=False, query='u1',
        )
        self.Recent.with_user(other).record_usage(
            action_id=False, res_model='res.partner', res_id=False, query='u2',
        )
        u1_recents = self.Recent.with_user(self.user).search([
            ('user_id', '=', self.user.id)
        ])
        self.assertEqual(len(u1_recents), 1)
        self.assertEqual(u1_recents.search_query, 'u1')

    def test_recent_capped_at_ten(self):
        for i in range(15):
            self.Recent.with_user(self.user).record_usage(
                action_id=False,
                res_model='res.partner',
                res_id=False,
                query=f'q{i}',
            )
        self.Recent.prune_for_user(self.user.id)
        recents = self.Recent.search([('user_id', '=', self.user.id)])
        self.assertLessEqual(len(recents), 10, 'recent should be capped at 10 per user')
