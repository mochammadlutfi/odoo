{
    'name': 'Data Exchange Suite',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Copy list data, record URL, and field values to clipboard in TSV/CSV/Markdown/JSON',
    'author': 'LutfiDev',
    'website': 'https://lutfidev.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ld_data_exchange/static/src/xml/copy_list_button.xml',
            'ld_data_exchange/static/src/js/copy_list_action.js',
            'ld_data_exchange/static/src/js/copy_url_patch.js',
            'ld_data_exchange/static/src/css/data_exchange.css',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
