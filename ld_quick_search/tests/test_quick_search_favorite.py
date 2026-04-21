from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestQuickSearchFavorite(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'QS Fav Tester',
            'login': 'qs_fav_tester',
        })
        cls.Favorite = cls.env['ld.quick_search.favorite']

    def test_create_favorite_forces_user(self):
        fav = self.Favorite.with_user(self.user).create({
            'label': 'Sale Orders',
            'sequence': 10,
        })
        self.assertEqual(fav.user_id, self.user)
        self.assertEqual(fav.label, 'Sale Orders')

    def test_create_rejects_user_spoofing(self):
        """user_id in vals is overwritten to current user — no spoofing allowed."""
        other = self.env['res.users'].create({
            'name': 'Spoof Target', 'login': 'spoof_target',
        })
        fav = self.Favorite.with_user(self.user).create({
            'label': 'spoofed',
            'user_id': other.id,
        })
        self.assertEqual(fav.user_id, self.user, 'user_id spoof must be rejected')

    def test_write_cannot_change_user(self):
        fav = self.Favorite.with_user(self.user).create({'label': 'A'})
        other = self.env['res.users'].create({
            'name': 'Other', 'login': 'write_spoof_target',
        })
        fav.with_user(self.user).write({'user_id': other.id})
        self.assertEqual(fav.user_id, self.user, 'write must drop user_id changes')

    def test_favorite_ordered_by_sequence(self):
        self.Favorite.with_user(self.user).create({'label': 'B', 'sequence': 20})
        self.Favorite.with_user(self.user).create({'label': 'A', 'sequence': 10})
        favs = self.Favorite.search([('user_id', '=', self.user.id)])
        self.assertEqual(favs[0].label, 'A', 'lowest sequence first')

    def test_per_user_isolation(self):
        other = self.env['res.users'].create({
            'name': 'QS Fav Other',
            'login': 'qs_fav_other',
        })
        self.Favorite.with_user(self.user).create({'label': 'u1'})
        self.Favorite.with_user(other).create({'label': 'u2'})
        u1_favs = self.Favorite.with_user(self.user).search([])
        labels = u1_favs.mapped('label')
        self.assertIn('u1', labels)
        self.assertNotIn('u2', labels, 'user should not see other users favorites')
