{
    'name': 'WhatsApp Quick Chat Indonesia',
    'version': '18.0.1.0.0',
    'summary': 'Click-to-WhatsApp buttons, Indonesian phone normalization (+62), '
               '10 Bahasa templates, bulk send. No API needed.',
    'description': '''
WhatsApp Quick Chat Indonesia
==============================

Click-to-WhatsApp dari Odoo untuk Contact, Sale Order, Purchase Order,
Invoice, dan Lead/Opportunity. Dirancang khusus untuk workflow Indonesia.

Fitur utama
-----------
* Tombol "Chat WA" di Partner, Sale, Purchase, Invoice, CRM Lead
* Normalisasi nomor Indonesia (+62): "0812-3456-7890" -> "6281234567890"
* 10 template Bahasa Indonesia siap pakai (Order, Invoice, Follow-up, dst.)
* Variable substitution: {{partner_name}}, {{amount}}, {{invoice_number}}, {{company_name}}
* Bulk send dari list view (open multi wa.me tabs)
* Click tracking di chatter + whatsapp.message.log
* 100% FREE, tanpa Twilio / Fonnte / WA Business API
* Mobile web -> langsung buka WhatsApp app

License: LGPL-3
    ''',
    'author': 'Mochammad Lutfi',
    'website': 'https://github.com/lutfidev',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
        'sale',
        'purchase',
        'account',
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_template_data.xml',
        'views/whatsapp_template_views.xml',
        'views/whatsapp_message_log_views.xml',
        'views/whatsapp_send_wizard_views.xml',
        'views/whatsapp_bulk_wizard_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/crm_lead_views.xml',
        'views/whatsapp_menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
