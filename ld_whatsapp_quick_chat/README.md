# WhatsApp Quick Chat Indonesia (`ld_whatsapp_quick_chat`)

**Odoo 18 · LGPL-3 · FREE**

Click-to-WhatsApp dari Odoo, dirancang untuk workflow Indonesia.
Tidak butuh API Twilio / Fonnte / WhatsApp Business — pakai link `wa.me` langsung.

## Fitur

- **5+ tombol Chat WA** di Partner, Sale Order, Purchase Order, Invoice, CRM Lead
- **Normalisasi nomor Indonesia** (+62, 62, 08, 8, dengan/tanpa dash/spasi)
- **10 template Bahasa Indonesia** siap pakai (Order, Invoice, Follow-up, dll.)
- **Variable substitution** Jinja2 melalui `mail.render.mixin` (sandbox Odoo)
- **Bulk send** dari list view Partner
- **Chat log** di chatter record + `whatsapp.message.log`
- **Mobile web** → langsung buka WhatsApp app

## Phone Normalization — Contoh

| Input                 | Output          |
|-----------------------|-----------------|
| `0812-3456-7890`      | `6281234567890` |
| `+62 812 3456 7890`   | `6281234567890` |
| `62812 3456 7890`     | `6281234567890` |
| `812 3456 7890`       | `6281234567890` |
| `8123456789`          | `628123456789`  |

## Templates

Edit atau tambah lewat menu **WhatsApp → Templates**. Variables:

- `{{object.name}}` — nama record (SO00123, INV/2026/001, dst.)
- `{{object.partner_id.name}}` — nama partner
- `{{object.amount_total}}` — total nilai (Sale/Invoice)
- `{{user.name}}` — nama user yang kirim
- `{{object.company_id.name}}` — nama company

## Install

```bash
# Pastikan `addons_new` ada di addons_path
./odoo-bin -i ld_whatsapp_quick_chat -d <db>
```

## Testing

```bash
./odoo-bin -i ld_whatsapp_quick_chat -d <db> --test-enable --stop-after-init
```

Test coverage target: ≥75%.

## Upgrade Path

Modul ini cukup untuk **manual chat 1-to-1 dan bulk kecil**.
Butuh automation (webhook incoming, auto-reply, scheduled broadcast,
API-based send)? Upgrade ke `ld_whatsapp_fonnte` / `ld_whatsapp_wablas` (F6).

## License

LGPL-3. Free for commercial use.
