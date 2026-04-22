{
    'name': 'Favicon Pro',
    'version': '18.0.1.0.0',
    'summary': 'Custom favicon per company with auto-generation from logo',
    'description': '''
        Favicon Pro for Odoo 18
        =======================
        - Auto-generate favicon dari company logo (Pillow)
        - Multi-company support: beda company beda favicon
        - Live preview di Settings sebelum save
        - Environment badge overlay (PROD/STAGING/UAT/DEV)
        - Apple touch icon + Android manifest auto-generate
        - Cache invalidation via timestamp query param
    ''',
    'author': 'Mochammad Lutfi',
    'website': 'https://lutfi.dev',
    'category': 'Website/Configuration',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'external_dependencies': {
        'python': ['Pillow'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ld_web_favicon_pro/static/src/js/favicon_preview.js',
            'ld_web_favicon_pro/static/src/xml/favicon_preview.xml',
        ],
        'web.assets_common': [
            'ld_web_favicon_pro/static/src/js/favicon_loader.js',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/main_screenshot.jpeg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
