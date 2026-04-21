import base64
import json
import time

from odoo import http
from odoo.http import request


class FaviconController(http.Controller):

    @http.route('/ld_favicon/favicon.ico', type='http', auth='public', sitemap=False)
    def company_favicon(self, **kw):
        company = request.env.company
        if company.favicon:
            favicon_data = base64.b64decode(company.favicon)
            headers = [
                ('Content-Type', 'image/x-icon'),
                ('Cache-Control', 'public, max-age=3600'),
                ('ETag', str(int(time.time() // 3600))),
            ]
            return request.make_response(favicon_data, headers=headers)

        # Fallback to default Odoo favicon
        from odoo.tools import file_open
        with file_open('web/static/img/favicon.ico', 'rb') as f:
            favicon_data = f.read()
        return request.make_response(favicon_data, headers=[
            ('Content-Type', 'image/x-icon'),
            ('Cache-Control', 'public, max-age=3600'),
        ])

    @http.route('/ld_favicon/apple-touch-icon.png', type='http', auth='public', sitemap=False)
    def apple_touch_icon(self, **kw):
        company = request.env.company
        if company.apple_touch_icon:
            data = base64.b64decode(company.apple_touch_icon)
            return request.make_response(data, headers=[
                ('Content-Type', 'image/png'),
                ('Cache-Control', 'public, max-age=86400'),
            ])
        return request.not_found()

    @http.route('/ld_favicon/android-chrome-192x192.png', type='http', auth='public', sitemap=False)
    def android_icon_192(self, **kw):
        company = request.env.company
        if company.android_icon_192:
            data = base64.b64decode(company.android_icon_192)
            return request.make_response(data, headers=[
                ('Content-Type', 'image/png'),
                ('Cache-Control', 'public, max-age=86400'),
            ])
        return request.not_found()

    @http.route('/ld_favicon/android-chrome-512x512.png', type='http', auth='public', sitemap=False)
    def android_icon_512(self, **kw):
        company = request.env.company
        if company.android_icon_512:
            data = base64.b64decode(company.android_icon_512)
            return request.make_response(data, headers=[
                ('Content-Type', 'image/png'),
                ('Cache-Control', 'public, max-age=86400'),
            ])
        return request.not_found()

    @http.route('/ld_favicon/site.webmanifest', type='http', auth='public', sitemap=False)
    def web_manifest(self, **kw):
        company = request.env.company
        manifest = {
            'name': company.name,
            'short_name': company.name[:12],
            'icons': [
                {
                    'src': f'/ld_favicon/android-chrome-192x192.png?v={int(time.time() // 3600)}',
                    'sizes': '192x192',
                    'type': 'image/png',
                },
                {
                    'src': f'/ld_favicon/android-chrome-512x512.png?v={int(time.time() // 3600)}',
                    'sizes': '512x512',
                    'type': 'image/png',
                },
            ],
            'theme_color': '#714B67',
            'background_color': '#ffffff',
            'display': 'standalone',
        }
        return request.make_response(
            json.dumps(manifest, indent=2),
            headers=[
                ('Content-Type', 'application/manifest+json'),
                ('Cache-Control', 'public, max-age=3600'),
            ],
        )

    @http.route('/ld_favicon/preview', type='json', auth='user')
    def favicon_preview(self, company_id=None, **kw):
        if not company_id:
            company_id = request.env.company.id
        result = request.env['res.company'].get_favicon_preview_data(int(company_id))
        return result
