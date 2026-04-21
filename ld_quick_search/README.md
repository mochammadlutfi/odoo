# Quick Search — Ctrl+K Command Palette for Odoo 18

Jump to any menu, action, or record in Odoo with **Ctrl+K** (or **Cmd+K** on
Mac). A VSCode / Slack / Notion style palette for Odoo that pays back its
install cost in 3 keystrokes.

## Highlights

- **Fuzzy search** — `salord` finds *Sale Orders*, `fakturr` finds *Invoices*
- **Multi-source**
  - *no prefix* → menu items (default)
  - `> text` → Odoo actions (`> new sale order`)
  - `# text` → settings shortcut
  - `@model text` → search records in a model (`@res.partner john`)
- **Recent & Favorites** — both cached in localStorage and persisted per-user
- **Keyboard-first** — ↑ ↓ Enter Esc, no mouse required
- **Security first** — record search honors `ir.model.access`, `ir.rule`, and
  an admin-controlled whitelist / blacklist. Hard-coded denylist for sensitive
  tables like `ir.config_parameter`, `auth.totp.device`, `res.users.log`.
- **Configurable shortcut** — avoid browser conflicts (e.g. Gmail's Ctrl+K)
- **Works in Community and Enterprise**, Odoo 18/19

## Usage

After installing, press **Ctrl+K** anywhere in the backend.

```
sales              → top menus matching "sales"
@res.partner john  → Contacts with "john" in the name
> journal entries  → the "Journal Entries" action
#users             → the Users settings shortcut
```

Navigate results with ↑ / ↓, open with **Enter**, close with **Esc**.

## Configuration

*Settings → Quick Search*

- **Keyboard Shortcut** (default `ctrl+k`)
- **Record Results Limit** (1–50)
- **Whitelist Models** — if set, only these models are searchable
- **Blacklist Models** — extra models to exclude

## Security model

`ld.quick_search.engine` runs every query as the calling user. On any access
failure it fails *closed* — returning an empty list. No record IDs are ever
leaked to clients that cannot read them.

Per-user `ir.rule` on `ld.quick_search.recent` and `ld.quick_search.favorite`
guarantees users only see their own data.

## License

LGPL-3. Free forever.

## Credits

Inspired by VSCode's Ctrl+P and Slack's Ctrl+K.
