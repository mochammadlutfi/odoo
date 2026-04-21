{
    'name': 'Environment Ribbon Pro',
    'version': '18.0.1.1.0',
    'summary': 'Visual environment indicator ribbon for Odoo backend (DEV/STG/UAT/PROD)',
    'description': '''
        Environment Ribbon Pro for Odoo 18
        ===================================
        - Config via Settings UI (tidak perlu edit config file)
        - 6 preset warna: DEV/STG/UAT/PROD/DEMO/TEST
        - Per-user dismiss (simpan di localStorage, muncul lagi besok)
        - Auto-detect dari environment variable ODOO_ENV
        - 4 posisi ribbon (top-right, top-left, bottom-right, diagonal)
        - Audit log akses production
        - Bahasa Indonesia tersedia
    ''',
    'author': 'Mochammad Lutfi',
    'website': '',
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
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
