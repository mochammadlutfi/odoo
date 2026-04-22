{
    'name': 'Environment Ribbon Pro',
    'version': '18.0.1.1.0',
    'summary': 'Visual environment indicator ribbon for Odoo backend (DEV/STG/UAT/PROD)',
    'description': '''
        Environment Ribbon Pro for Odoo 18
        ===================================
        - Configure via Settings UI (no config file editing needed)
        - 6 preset color environments: DEV / STAGING / UAT / PRODUCTION / DEMO / TEST
        - Per-user dismiss (stored in localStorage, reappears the next day)
        - Auto-detect via the ODOO_ENV environment variable
        - 4 ribbon styles (Bar / Corner / Vertical / Banner) x 4 positions
        - Production access audit log
        - Indonesian translation included
    ''',
    'author': 'Mochammad Lutfi',
    'website': 'https://lutfi.dev',
    'category': 'Technical',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/env_ribbon_audit_log_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ld_env_ribbon_pro/static/src/scss/ribbon.scss',
            'ld_env_ribbon_pro/static/src/js/ribbon.js',
            'ld_env_ribbon_pro/static/src/xml/ribbon.xml',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
