/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

const MODE_CYCLE = ["light", "dark", "auto", "schedule"];
const MODE_LABELS = {
    // Thunks defer _t() until the factory is invoked so the right locale
    // is active at render time.
    light: () => _t("Light Mode"),
    dark: () => _t("Dark Mode"),
    auto: () => _t("Auto (Follow OS)"),
    schedule: () => _t("Schedule"),
};

/**
 * User-menu item that cycles through dark-mode preferences.
 *
 * The `user_menuitems` registry re-invokes every factory on each dropdown
 * open (see web/src/webclient/user_menu/user_menu.js::getElements), so the
 * `description` reflects the current state as long as the dropdown has
 * been reopened since the last change. On mode changes that do NOT trigger
 * a reload (e.g. auto → dark while the OS already prefers dark), closing
 * and reopening the menu refreshes the label.
 */
function darkModeMenuItem(env) {
    const service = env.services.ldDarkMode;
    const current = service ? service.getPreference().mode : "auto";
    const label = (MODE_LABELS[current] || MODE_LABELS.auto)();

    return {
        type: "item",
        id: "ld_dark_mode_toggle",
        description: _t("Dark Mode: %s", label),
        callback: async () => {
            if (!service) {
                return;
            }
            const state = service.getPreference();
            const idx = MODE_CYCLE.indexOf(state.mode);
            const next = MODE_CYCLE[(idx + 1) % MODE_CYCLE.length];
            await service.setPreference({ mode: next });
        },
        sequence: 55,
    };
}

registry.category("user_menuitems").add("ld_dark_mode_toggle", darkModeMenuItem);
