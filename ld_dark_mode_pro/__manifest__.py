{
    'name': 'Dark Mode Pro',
    'version': '18.0.1.0.0',
    'summary': 'Persistent, schedulable dark mode for Odoo 18 — auto-detect OS theme, no flicker, consistent across backend, POS, reports',
    'description': '''
Dark Mode Pro for Odoo 18
=========================

Fixes Odoo 18 built-in dark mode shortcomings:

- Persistent after logout/login — no manual refresh
- Auto-switch via OS `prefers-color-scheme`
- Schedule mode (e.g., dark 19:00–07:00)
- Consistent across Backend, POS, Reports preview, Wizards
- No flicker / FOUC on login page
- Per-user preference saved in `res.users`
- Admin defaults scoped by company, groups, and departments
- Pure Odoo + JS — no external dependencies
    ''',
    'author': 'Mochammad Lutfi',
    'website': 'https://github.com/mochammadlutfi',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/ld_dark_mode_config_views.xml',
        'views/ld_dark_mode_menus.xml',
        'views/web_login_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ld_dark_mode_pro/static/src/scss/variables.scss',
            'ld_dark_mode_pro/static/src/scss/wizard_dark.scss',
            'ld_dark_mode_pro/static/src/scss/report_preview_dark.scss',
            'ld_dark_mode_pro/static/src/js/dark_mode_service.js',
            'ld_dark_mode_pro/static/src/js/dark_mode_schedule.js',
            'ld_dark_mode_pro/static/src/js/dark_mode_toggle.js',
            'ld_dark_mode_pro/static/src/xml/dark_mode_toggle.xml',
        ],
        'web.assets_frontend': [
            'ld_dark_mode_pro/static/src/scss/variables.scss',
            'ld_dark_mode_pro/static/src/scss/login_dark.scss',
            'ld_dark_mode_pro/static/src/scss/report_preview_dark.scss',
            'ld_dark_mode_pro/static/src/js/dark_mode_early.js',
            'ld_dark_mode_pro/static/src/js/login_toggle.js',
        ],
        'point_of_sale.assets_prod': [
            'ld_dark_mode_pro/static/src/pos/pos_dark.scss',
        ],
        'point_of_sale.assets_debug': [
            'ld_dark_mode_pro/static/src/pos/pos_dark.scss',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
