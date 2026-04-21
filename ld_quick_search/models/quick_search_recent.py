from odoo import api, fields, models


RECENT_LIMIT_PER_USER = 10
MAX_STR_LEN = 256


class QuickSearchRecent(models.Model):
    _name = 'ld.quick_search.recent'
    _description = 'Recent Quick Search'
    _order = 'last_used desc'

    user_id = fields.Many2one(
        'res.users',
        required=True,
        ondelete='cascade',
        default=lambda self: self.env.user,
        index=True,
    )
    action_id = fields.Many2one('ir.actions.actions', ondelete='set null')
    res_model = fields.Char()
    res_id = fields.Integer()
    search_query = fields.Char()
    last_used = fields.Datetime(default=fields.Datetime.now)
    use_count = fields.Integer(default=1)

    @api.model_create_multi
    def create(self, vals_list):
        uid = self.env.uid
        for vals in vals_list:
            vals['user_id'] = uid  # force — never allow spoofing
            self._sanitize_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        # user_id must never be changed post-create.
        vals.pop('user_id', None)
        self._sanitize_vals(vals)
        return super().write(vals)

    @staticmethod
    def _sanitize_vals(vals):
        for key in ('res_model', 'search_query'):
            v = vals.get(key)
            if isinstance(v, str) and len(v) > MAX_STR_LEN:
                vals[key] = v[:MAX_STR_LEN]
        if 'res_id' in vals and vals['res_id'] is not False and not isinstance(vals['res_id'], int):
            vals['res_id'] = False

    @api.model
    def record_usage(self, action_id=False, res_model=False, res_id=False, query=False):
        """Upsert a recent entry for the current user.

        Silently drops disallowed models (anything in the engine blacklist).
        Returns the stored record or an empty recordset on bad input.
        """
        user = self.env.user

        # Type discipline — reject anything exotic.
        if action_id and not isinstance(action_id, int):
            action_id = False
        if res_id and not isinstance(res_id, int):
            res_id = False
        if res_model and not isinstance(res_model, str):
            return self.browse()
        if query and not isinstance(query, str):
            return self.browse()

        # Model allowed? Use the engine's policy.
        if res_model:
            engine = self.env['ld.quick_search.engine']
            if not engine._model_allowed(res_model):
                res_model = False
                res_id = False

        # Trim strings.
        if isinstance(res_model, str):
            res_model = res_model[:MAX_STR_LEN]
        if isinstance(query, str):
            query = query[:MAX_STR_LEN]

        domain = [
            ('user_id', '=', user.id),
            ('action_id', '=', action_id or False),
            ('res_model', '=', res_model or False),
            ('res_id', '=', res_id or False),
            ('search_query', '=', query or False),
        ]
        existing = self.sudo().search(domain, limit=1)
        if existing:
            existing.write({
                'use_count': existing.use_count + 1,
                'last_used': fields.Datetime.now(),
            })
            rec = existing
        else:
            rec = self.sudo().create({
                'action_id': action_id or False,
                'res_model': res_model or False,
                'res_id': res_id or False,
                'search_query': query or False,
            })
        # Prune unconditionally so upsert-with-fresh-rows also bounds storage.
        self.prune_for_user(user.id)
        return rec

    @api.model
    def prune_for_user(self, user_id):
        """Keep only the N most recent entries per user."""
        recents = self.sudo().search(
            [('user_id', '=', user_id)],
            order='last_used desc',
        )
        if len(recents) > RECENT_LIMIT_PER_USER:
            recents[RECENT_LIMIT_PER_USER:].unlink()
