from odoo import fields, models


class LdDarkModeConfig(models.Model):
    _name = 'ld.dark_mode.config'
    _description = 'Dark Mode Default Policy'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    apply_to_company_ids = fields.Many2many(
        'res.company',
        'ld_dark_mode_config_company_rel',
        'config_id', 'company_id',
        string='Companies',
        help='Companies this default applies to. Empty = all companies.',
    )
    apply_to_department_ids = fields.Many2many(
        'hr.department',
        'ld_dark_mode_config_department_rel',
        'config_id', 'department_id',
        string='Departments',
        help='Departments this default applies to. Empty = all departments.',
    )
    apply_to_group_ids = fields.Many2many(
        'res.groups',
        'ld_dark_mode_config_group_rel',
        'config_id', 'group_id',
        string='User Groups',
        help='Groups this default applies to. Empty = all groups.',
    )

    default_mode = fields.Selection(
        [('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto (Follow OS)')],
        string='Default Mode',
        default='auto',
        required=True,
    )
    whitelist_modules = fields.Char(
        string='Whitelist Modules',
        help='Comma-separated technical names of modules/actions that should '
             'stay in light mode even when dark is active. Applies to report '
             'preview iframes and known wizard action tags.',
    )

    def get_whitelist_list(self):
        """Return the comma-separated whitelist as a cleaned list of strings."""
        self.ensure_one()
        if not self.whitelist_modules:
            return []
        return [m.strip() for m in self.whitelist_modules.split(',') if m.strip()]

    @staticmethod
    def _matches_any(relation_ids, user_ids):
        """Empty relation = match-all; otherwise require intersection."""
        if not relation_ids:
            return True
        return bool(set(relation_ids.ids) & set(user_ids.ids))

    def _get_default_for_user(self, user):
        """Return the first active config that applies to `user`, or empty."""
        user.ensure_one()
        user_department_ids = user.employee_ids.mapped('department_id')
        for config in self.search([('active', '=', True)]):
            if not self._matches_any(config.apply_to_company_ids, user.company_ids):
                continue
            if not self._matches_any(config.apply_to_group_ids, user.groups_id):
                continue
            if not self._matches_any(
                config.apply_to_department_ids, user_department_ids,
            ):
                continue
            return config
        return self.browse()
