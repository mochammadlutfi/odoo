from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDarkModeConfig(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Config = cls.env['ld.dark_mode.config']
        cls.company = cls.env.ref('base.main_company')
        cls.group_user = cls.env.ref('base.group_user')
        cls.group_portal = cls.env.ref('base.group_portal')
        cls.user = cls.env['res.users'].create({
            'name': 'Config Test User',
            'login': 'ld_dm_config_user',
            'groups_id': [(6, 0, [cls.group_user.id])],
            'company_id': cls.company.id,
            'company_ids': [(6, 0, [cls.company.id])],
        })

    def test_empty_scope_matches_all(self):
        cfg = self.Config.create({
            'name': 'Global',
            'default_mode': 'dark',
        })
        matched = self.Config._get_default_for_user(self.user)
        self.assertEqual(matched, cfg)

    def test_company_scope_matching(self):
        cfg = self.Config.create({
            'name': 'Main Company',
            'default_mode': 'dark',
            'apply_to_company_ids': [(6, 0, [self.company.id])],
        })
        self.assertEqual(
            self.Config._get_default_for_user(self.user),
            cfg,
        )

    def test_group_scope_mismatch_returns_empty(self):
        self.Config.create({
            'name': 'Portal Only',
            'default_mode': 'dark',
            'apply_to_group_ids': [(6, 0, [self.group_portal.id])],
        })
        self.assertFalse(self.Config._get_default_for_user(self.user))

    def test_inactive_config_ignored(self):
        self.Config.create({
            'name': 'Archived',
            'default_mode': 'dark',
            'active': False,
        })
        self.assertFalse(self.Config._get_default_for_user(self.user))

    def test_sequence_controls_priority(self):
        cfg_low = self.Config.create({
            'name': 'Low Priority',
            'default_mode': 'light',
            'sequence': 20,
        })
        cfg_high = self.Config.create({
            'name': 'High Priority',
            'default_mode': 'dark',
            'sequence': 5,
        })
        matched = self.Config._get_default_for_user(self.user)
        self.assertEqual(matched, cfg_high)
        self.assertNotEqual(matched, cfg_low)

    def test_whitelist_modules_parsing(self):
        cfg = self.Config.create({
            'name': 'WL',
            'default_mode': 'dark',
            'whitelist_modules': 'account_reports, website_sale ,pos_blackbox ',
        })
        self.assertEqual(
            cfg.get_whitelist_list(),
            ['account_reports', 'website_sale', 'pos_blackbox'],
        )

    def test_whitelist_modules_empty(self):
        cfg = self.Config.create({
            'name': 'NoWL',
            'default_mode': 'auto',
        })
        self.assertEqual(cfg.get_whitelist_list(), [])

    def test_policy_applied_on_user_creation(self):
        """A matching active policy sets the default preference on new users
        that didn't explicitly pick one."""
        self.Config.create({
            'name': 'Company-wide Dark',
            'default_mode': 'dark',
            'apply_to_company_ids': [(6, 0, [self.company.id])],
        })
        new_user = self.env['res.users'].create({
            'name': 'Fresh User',
            'login': 'ld_dm_fresh_user',
        })
        self.assertEqual(new_user.dark_mode_preference, 'dark')

    def test_explicit_preference_wins_over_policy(self):
        self.Config.create({
            'name': 'Company-wide Dark',
            'default_mode': 'dark',
        })
        new_user = self.env['res.users'].create({
            'name': 'Opinionated User',
            'login': 'ld_dm_opinionated_user',
            'dark_mode_preference': 'light',
        })
        self.assertEqual(new_user.dark_mode_preference, 'light')

    def test_department_scope_matching(self):
        department = self.env['hr.department'].create({'name': 'IT Dept'})
        self.env['hr.employee'].create({
            'name': 'Emp',
            'user_id': self.user.id,
            'department_id': department.id,
        })
        cfg = self.Config.create({
            'name': 'IT Policy',
            'default_mode': 'dark',
            'apply_to_department_ids': [(6, 0, [department.id])],
        })
        self.assertEqual(
            self.Config._get_default_for_user(self.user),
            cfg,
        )
