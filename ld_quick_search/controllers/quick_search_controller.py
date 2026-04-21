import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

ALLOWED_SCOPES = {'menu', 'action', 'record'}
MAX_QUERY_LENGTH = 200
MAX_MODEL_LENGTH = 128


def _coerce_str(value, max_len):
    if not isinstance(value, str):
        return ''
    return value[:max_len]


def _coerce_int_or_false(value):
    if isinstance(value, bool):
        # bool is subclass of int; treat False/True as "no id"
        return False
    if isinstance(value, int):
        return value
    return False


class QuickSearchController(http.Controller):

    @http.route(
        '/ld_quick_search/search',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def search(self, query='', scope='menu', model=None, **_ignored):
        """JSON-RPC endpoint. Returns {'results': [...]} or raises for bad input."""
        if not isinstance(query, str):
            raise ValueError('query must be a string')
        if len(query) > MAX_QUERY_LENGTH:
            query = query[:MAX_QUERY_LENGTH]
        if scope not in ALLOWED_SCOPES:
            raise ValueError(f'unknown scope: {scope!r}')
        if model is not None:
            if not isinstance(model, str):
                raise ValueError('model must be a string or null')
            if len(model) > MAX_MODEL_LENGTH:
                raise ValueError('model name too long')

        engine = request.env['ld.quick_search.engine']
        results = engine.search_all(query=query, scope=scope, model=model)
        return {'results': results}

    @http.route(
        '/ld_quick_search/record_usage',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def record_usage(self, action_id=False, res_model=False, res_id=False, query=False, **_ignored):
        action_id = _coerce_int_or_false(action_id)
        res_id = _coerce_int_or_false(res_id)
        res_model = _coerce_str(res_model, MAX_MODEL_LENGTH) if res_model else False
        query = _coerce_str(query, MAX_QUERY_LENGTH) if query else False

        Recent = request.env['ld.quick_search.recent']
        rec = Recent.record_usage(
            action_id=action_id or False,
            res_model=res_model or False,
            res_id=res_id or False,
            query=query or False,
        )
        return {'id': rec.id if rec else False}

    @http.route(
        '/ld_quick_search/recents',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def recents(self, **_ignored):
        Recent = request.env['ld.quick_search.recent']
        rows = Recent.search(
            [('user_id', '=', request.env.user.id)],
            limit=10,
            order='last_used desc',
        )
        return {
            'results': [
                {
                    'id': r.id,
                    'type': 'recent',
                    'label': r.search_query or (r.res_model or ''),
                    'res_model': r.res_model,
                    'res_id': r.res_id,
                    'action_id': r.action_id.id if r.action_id else False,
                    'use_count': r.use_count,
                }
                for r in rows
            ],
        }

    @http.route(
        '/ld_quick_search/favorites',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def favorites(self, **_ignored):
        Fav = request.env['ld.quick_search.favorite']
        rows = Fav.search(
            [('user_id', '=', request.env.user.id)],
            order='sequence, id',
        )
        return {
            'results': [
                {
                    'id': f.id,
                    'type': 'favorite',
                    'label': f.label,
                    'action_id': f.action_id.id if f.action_id else False,
                    'res_model': f.res_model,
                    'res_id': f.res_id,
                }
                for f in rows
            ],
        }
