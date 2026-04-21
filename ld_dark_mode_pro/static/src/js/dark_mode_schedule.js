/** @odoo-module **/

import { registry } from "@web/core/registry";

const CHECK_INTERVAL_MS = 60_000;

/**
 * Background service that re-evaluates schedule mode every minute.
 * When the effective mode transitions (e.g., 18:59 light → 19:00 dark),
 * the dark-mode service triggers a single page reload so the dark bundle
 * loads.
 */
const scheduleTickService = {
    dependencies: ["ldDarkMode"],
    start(env, { ldDarkMode }) {
        setInterval(() => {
            try {
                const state = ldDarkMode.getPreference();
                if (state.mode === "schedule" || state.mode === "auto") {
                    ldDarkMode.applyEffective();
                }
            } catch (_) {
                // Never let a scheduler tick crash.
            }
        }, CHECK_INTERVAL_MS);
        return {};
    },
};

registry.category("services").add("ldDarkModeScheduleTick", scheduleTickService);
