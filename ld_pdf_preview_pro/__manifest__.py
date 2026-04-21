{
    'name': 'PDF Preview Pro',
    'version': '18.0.1.0.0',
    'summary': 'Preview PDF inline di modal — mobile first, Bahasa Indonesia, direct print',
    'description': """
PDF Preview Pro
===============
Preview PDF attachment langsung di modal dialog tanpa download dulu.
Menggunakan PDF.js yang sudah bundled di Odoo 18.

Fitur:
- Preview PDF inline (OWL modal fullscreen)
- Navigasi halaman (prev/next button + swipe di mobile)
- Zoom in/out (25% step, max 300%)
- Direct print via browser print dialog
- Download langsung dari toolbar
- Dark mode otomatis (ikut system preference)
- UI Bahasa Indonesia
    """,
    'author': 'Luduh Dev',
    'website': '',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'depends': ['mail', 'web'],
    'assets': {
        'web.assets_backend': [
            'ld_pdf_preview_pro/static/src/scss/pdf_preview.scss',
            'ld_pdf_preview_pro/static/src/xml/pdf_preview_dialog.xml',
            'ld_pdf_preview_pro/static/src/js/pdf_preview_dialog.js',
            'ld_pdf_preview_pro/static/src/js/attachment_list_patch.js',
            'ld_pdf_preview_pro/static/src/js/report_action_patch.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
