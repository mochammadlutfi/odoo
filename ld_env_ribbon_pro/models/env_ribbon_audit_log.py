from odoo import fields, models


class EnvRibbonAuditLog(models.Model):
    _name = 'env.ribbon.audit.log'
    _description = 'Environment Ribbon Production Access Log'
    _order = 'access_time desc'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    access_time = fields.Datetime(string='Access Time', default=fields.Datetime.now, required=True)
    ip_address = fields.Char(string='IP Address')
    user_agent = fields.Char(string='User Agent')
    action_type = fields.Selection(
        selection=[
            ('login', 'Login'),
            ('session', 'Session Start'),
        ],
        string='Action',
        default='session',
    )
