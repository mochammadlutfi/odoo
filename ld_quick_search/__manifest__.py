{
    'name': 'Quick Search Ctrl+K',
    'version': '18.0.1.0.0',
    'summary': 'VSCode-style Ctrl+K palette to jump to any menu, action, or record.',
    'description': '''
Quick Search for Odoo 18
========================

Press **Ctrl+K** (or Cmd+K on Mac) from anywhere in the Odoo backend to open a
fast, fuzzy command palette that searches:

- Menu items (type anything)
- Records across models (prefix ``@``, e.g. ``@partner john``)
- Actions (prefix ``>``, e.g. ``> new sale order``)
- Settings (prefix ``#``)

Features
--------
- Fuzzy matching — typo tolerant (``salord`` → Sale Orders)
- Recent searches (per-user, last 10)
- Favorites / pinned items (per-user)
- Keyboard-only navigation (↑ ↓ Enter Esc)
- Respects Odoo access rights (ACL) on record search
- Admin whitelist / blacklist models
- Configurable shortcut
- Works in Community and Enterprise

License
-------
LGPL-3. FREE forever.
    ''',
    'author': 'Mochammad Lutfi',
    'website': 'https://github.com/mochammadlutfi',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/quick_search_recent_views.xml',
        'views/quick_search_favorite_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ld_quick_search/static/src/scss/quick_search.scss',
            'ld_quick_search/static/src/js/fuzzy.js',
            'ld_quick_search/static/src/js/quick_search_service.js',
            'ld_quick_search/static/src/js/quick_search_palette.js',
            'ld_quick_search/static/src/xml/quick_search_palette.xml',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
