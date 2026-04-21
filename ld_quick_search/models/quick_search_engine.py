import logging

from odoo import api, models
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

# Models that MUST NEVER be searchable for security reasons, regardless of ACL.
# These either hold secrets or leak system internals, and their access_rights
# check is not strict enough to catch display_name leakage (e.g. res.users
# leaks login via display_name).
HARD_DENYLIST = frozenset({
    # Auth / secrets
    'res.users',
    'res.users.log',
    'auth.totp.device',
    'auth.totp.wizard',
    # Infrastructure with secrets
    'ir.mail_server',
    'fetchmail.server',
    'ir.config_parameter',
    # Security config
    'ir.rule',
    'ir.model.access',
    # Scheduled / automation code
    'ir.cron',
    'base.automation',
    # Attachments often contain private data
    'ir.attachment',
    # Internals
    'mail.tracking.value',
    'ir.model',
    'ir.model.fields',
})

DEFAULT_RECORD_LIMIT = 10
MENU_RESULT_LIMIT = 40
ACTION_RESULT_LIMIT = 20


class QuickSearchEngine(models.AbstractModel):
    """Stateless search engine used by the controller.

    All methods run as the current user — never escalate privileges.
    ACL enforcement is delegated to the ORM. On any access failure we fail
    *closed* (empty results) so the palette never leaks record identifiers.
    """

    _name = 'ld.quick_search.engine'
    _description = 'Quick Search Engine'

    @api.model
    def _get_blacklist(self):
        param = self.env['ir.config_parameter'].sudo().get_param(
            'ld_quick_search.blacklist_models', default='',
        )
        user_blacklist = {m.strip() for m in (param or '').split(',') if m.strip()}
        return HARD_DENYLIST | user_blacklist

    @api.model
    def _get_whitelist(self):
        param = self.env['ir.config_parameter'].sudo().get_param(
            'ld_quick_search.whitelist_models', default='',
        )
        return {m.strip() for m in (param or '').split(',') if m.strip()}

    @api.model
    def _model_allowed(self, model_name):
        if not model_name or not isinstance(model_name, str):
            return False
        if model_name in self._get_blacklist():
            return False
        whitelist = self._get_whitelist()
        if whitelist and model_name not in whitelist:
            return False
        if model_name not in self.env:
            return False
        return True

    @api.model
    def _get_record_limit(self):
        param = self.env['ir.config_parameter'].sudo().get_param(
            'ld_quick_search.record_limit', default=DEFAULT_RECORD_LIMIT,
        )
        try:
            return max(1, min(50, int(param)))
        except (TypeError, ValueError):
            return DEFAULT_RECORD_LIMIT

    @api.model
    def search_menus(self, query):
        """Return menu entries the user can see. Odoo filters by groups_id.

        The fuzzy match happens on the JS side — here we just ship a
        pre-filtered index small enough for 150ms round-trip.
        """
        query = (query or '').strip().lower()
        Menu = self.env['ir.ui.menu']
        try:
            all_menus = Menu.search([('action', '!=', False)])
        except AccessError:
            return []
        results = []
        for menu in all_menus:
            full = (menu.complete_name or '').lower()
            if query and query not in full and query not in (menu.name or '').lower():
                continue
            action_ref = menu.action
            results.append({
                'type': 'menu',
                'id': menu.id,
                'label': menu.name or '',
                'path': menu.complete_name or '',
                'action_id': action_ref.id if action_ref else False,
                'action_model': action_ref._name if action_ref else False,
                'icon': menu.web_icon or '',
            })
            if len(results) >= MENU_RESULT_LIMIT:
                break
        return results

    @api.model
    def search_actions(self, query):
        query = (query or '').strip()
        if not query:
            return []
        ActWindow = self.env['ir.actions.act_window']
        try:
            actions = ActWindow.search(
                [('name', 'ilike', query)],
                limit=ACTION_RESULT_LIMIT,
            )
        except AccessError:
            return []
        return [
            {
                'type': 'action',
                'id': action.id,
                'label': action.name,
                'res_model': action.res_model,
                'view_mode': action.view_mode,
            }
            for action in actions
        ]

    @api.model
    def search_records(self, model, query):
        """Fuzzy search records in ``model``. Returns [] on any access issue."""
        if not self._model_allowed(model):
            return []
        query = (query or '').strip()
        if not query:
            return []
        try:
            Model = self.env[model]
            Model.check_access_rights('read', raise_exception=True)
        except (KeyError, AccessError, UserError):
            return []

        rec_name = Model._rec_name or 'name'
        if rec_name not in Model._fields:
            return []

        try:
            records = Model.search(
                [(rec_name, 'ilike', query)],
                limit=self._get_record_limit(),
            )
        except (AccessError, UserError) as exc:
            _logger.debug('quick_search denied on %s: %s', model, exc)
            return []

        results = []
        for rec in records:
            try:
                label = rec.display_name or str(rec.id)
            except AccessError:
                continue
            results.append({
                'type': 'record',
                'id': rec.id,
                'model': model,
                'label': label,
            })
        return results

    @api.model
    def search_all(self, query, scope='menu', model=None):
        """Dispatch by scope. Controller validates scope before calling."""
        if scope == 'menu':
            return self.search_menus(query)
        if scope == 'action':
            return self.search_actions(query)
        if scope == 'record':
            return self.search_records(model or '', query)
        return []
