# Dark Mode Pro (`ld_dark_mode_pro`)

Persistent, schedulable dark mode for Odoo 18. Fixes the flicker and
inconsistency issues of the built-in dark mode and adds auto OS detection
plus time-based scheduling.

## What this module adds

- **Persistence** — survives logout/login, no manual refresh needed.
- **OS auto-detect** — follows `prefers-color-scheme`.
- **Schedule mode** — e.g. dark from 19:00 to 07:00 (wrap-around supported).
- **Login page coverage** — no white flash before asset bundles load.
- **Consistent across screens** — backend, POS, report preview, wizards.
- **Admin defaults** — scope a default mode by company, department, or user group.

## Installation

1. Drop the `ld_dark_mode_pro` folder into any `addons_path`.
2. Update the apps list and install the **Dark Mode Pro** module.
3. Reload the browser.

## Usage

### For users

- Open your user menu (top-right) → **Dark Mode**. Click cycles through
  `Light → Dark → Auto → Schedule`.
- In **Preferences → Dark Mode** you can set custom schedule hours (float
  24-hour, e.g. `19.5` = 19:30).

### For admins

- Navigate to **Settings → Technical → Dark Mode → Dark Mode Policies** to
  create scoped defaults (by company, department, and/or user groups).
- The policy sets a default for users that have not yet chosen their own
  preference.

## How it works

Odoo 18's dark mode is cookie-driven: `color_scheme=dark` tells the server
to serve the `web.assets_web_dark` bundle. This module:

1. Injects an inline head script into every page that reads
   `localStorage.ldDarkMode`, resolves the effective mode (accounting for
   OS preference + schedule), sets a `data-ld-dark` attribute **before first
   paint**, and — if needed — updates the cookie and reloads once (guarded
   by a session flag to prevent reload loops).
2. Adds an OWL user-menu item that persists the preference via ORM
   (`res.users.dark_mode_preference`) and forces a single reload to load
   the correct asset bundle.
3. Runs a 60-second client-side tick to re-evaluate schedule/auto modes
   while the tab is open.
4. Layers SCSS fixes for the login page, report preview iframe shell,
   modal dialogs, and POS — all scoped under `html[data-ld-dark="1"]`.

## Testing

```bash
odoo-bin -d <db> -i ld_dark_mode_pro --test-enable --stop-after-init
```

Runs ~20 unit/integration tests covering:

- `_is_within_schedule` pure function (boundary + wrap-around cases).
- `res.users` field defaults + self-writeable exposure.
- `ld.dark_mode.config` scope matching and whitelist parsing.
- `/ld_dark_mode/set` controller cookie behaviour.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Still flickering on login | Clear browser cache; ensure module is installed (not just present). |
| Toggle does nothing | Check browser console for RPC errors; the service falls back to localStorage-only when write fails. |
| Schedule not triggering | Verify that `localStorage.ldDarkMode.mode === "schedule"` and your system clock is correct. |
| Want to reset | Clear the `color_scheme` cookie and `ldDarkMode` localStorage key, then reload. |

## License

LGPL-3

## Author

Mochammad Lutfi
