from odoo import api, fields, models


MAX_STR_LEN = 256


class QuickSearchFavorite(models.Model):
    _name = 'ld.quick_search.favorite'
    _description = 'Favorite Quick Search'
    _order = 'sequence, id'

    user_id = fields.Many2one(
        'res.users',
        required=True,
        ondelete='cascade',
        default=lambda self: self.env.user,
        index=True,
    )
    label = fields.Char(required=True)
    action_id = fields.Many2one('ir.actions.actions', ondelete='set null')
    res_model = fields.Char()
    res_id = fields.Integer()
    sequence = fields.Integer(default=10)

    @api.model_create_multi
    def create(self, vals_list):
        uid = self.env.uid
        for vals in vals_list:
            vals['user_id'] = uid
            self._sanitize_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        vals.pop('user_id', None)
        self._sanitize_vals(vals)
        return super().write(vals)

    @staticmethod
    def _sanitize_vals(vals):
        for key in ('label', 'res_model'):
            v = vals.get(key)
            if isinstance(v, str) and len(v) > MAX_STR_LEN:
                vals[key] = v[:MAX_STR_LEN]
        if 'res_id' in vals and vals['res_id'] is not False and not isinstance(vals['res_id'], int):
            vals['res_id'] = False
