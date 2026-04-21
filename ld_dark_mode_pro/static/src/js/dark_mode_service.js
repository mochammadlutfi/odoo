/** @odoo-module **/

import { registry } from "@web/core/registry";
import { cookie } from "@web/core/browser/cookie";

const LOCAL_KEY = "ldDarkMode";
const RELOAD_FLAG = "ldDarkReloaded";
const VALID = new Set(["light", "dark", "auto", "schedule"]);

function _clampHour(value, fallback) {
    if (typeof value !== "number" || Number.isNaN(value) || value < 0 || value >= 24) {
        return fallback;
    }
    return value;
}

function _readLocal() {
    let parsed = null;
    try {
        const raw = window.localStorage.getItem(LOCAL_KEY);
        parsed = raw ? JSON.parse(raw) : null;
    } catch (_) {
        return null;
    }
    if (!parsed) {
        return null;
    }
    return {
        mode: VALID.has(parsed.mode) ? parsed.mode : "auto",
        scheduleStart: _clampHour(parsed.scheduleStart, 19),
        scheduleEnd: _clampHour(parsed.scheduleEnd, 7),
    };
}

function _writeLocal(state) {
    try {
        window.localStorage.setItem(LOCAL_KEY, JSON.stringify(state));
    } catch (_) {
        // Storage quota, private mode, etc. — ignore silently.
    }
}

function _isWithinSchedule(nowHour, start, end) {
    if (start === end) {
        return false;
    }
    if (start < end) {
        return nowHour >= start && nowHour < end;
    }
    return nowHour >= start || nowHour < end;
}

/**
 * Resolve the effective 'light' | 'dark' given a preference record.
 * @param {{mode: string, scheduleStart: number, scheduleEnd: number}} state
 * @returns {'light' | 'dark'}
 */
export function resolveEffective(state) {
    const pref = (state && state.mode) || "auto";
    if (pref === "dark") {
        return "dark";
    }
    if (pref === "light") {
        return "light";
    }
    if (pref === "auto") {
        const mq = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
        return mq && mq.matches ? "dark" : "light";
    }
    if (pref === "schedule") {
        const now = new Date();
        const hour = now.getHours() + now.getMinutes() / 60;
        const start = state && typeof state.scheduleStart === "number" ? state.scheduleStart : 19;
        const end = state && typeof state.scheduleEnd === "number" ? state.scheduleEnd : 7;
        return _isWithinSchedule(hour, start, end) ? "dark" : "light";
    }
    return "light";
}

export const ldDarkModeService = {
    dependencies: ["orm", "user"],

    start(env, { orm, user }) {
        let state = _readLocal() || {
            mode: "auto",
            scheduleStart: 19,
            scheduleEnd: 7,
        };

        function currentCookieMode() {
            return cookie.get("color_scheme") || "light";
        }

        async function loadFromUser() {
            try {
                const [record] = await orm.read("res.users", [user.userId], [
                    "dark_mode_preference",
                    "dark_mode_schedule_start",
                    "dark_mode_schedule_end",
                ]);
                if (record) {
                    state = {
                        mode: record.dark_mode_preference || "auto",
                        scheduleStart: record.dark_mode_schedule_start ?? 19,
                        scheduleEnd: record.dark_mode_schedule_end ?? 7,
                    };
                    _writeLocal(state);
                }
            } catch (_) {
                // Fall back to local state — service must never throw.
            }
        }

        function applyEffective({ reload = true } = {}) {
            const effective = resolveEffective(state);
            const current = currentCookieMode();
            if (effective === "dark") {
                document.documentElement.setAttribute("data-ld-dark", "1");
            } else {
                document.documentElement.removeAttribute("data-ld-dark");
            }
            if (current !== effective) {
                cookie.set("color_scheme", effective, 365 * 24 * 60 * 60);
                if (reload) {
                    try {
                        window.sessionStorage.setItem(RELOAD_FLAG, "1");
                    } catch (_) {}
                    window.location.reload();
                    return true;
                }
            } else {
                try {
                    window.sessionStorage.removeItem(RELOAD_FLAG);
                } catch (_) {}
            }
            return false;
        }

        async function setPreference({ mode, scheduleStart, scheduleEnd } = {}) {
            if (!VALID.has(mode)) {
                throw new Error(`Invalid dark mode: ${mode}`);
            }
            state = {
                mode,
                scheduleStart: typeof scheduleStart === "number" ? scheduleStart : state.scheduleStart,
                scheduleEnd: typeof scheduleEnd === "number" ? scheduleEnd : state.scheduleEnd,
            };
            _writeLocal(state);
            try {
                await orm.write("res.users", [user.userId], {
                    dark_mode_preference: state.mode,
                    dark_mode_schedule_start: state.scheduleStart,
                    dark_mode_schedule_end: state.scheduleEnd,
                });
            } catch (_) {
                // RPC failures should not break the UX — local state still wins.
            }
            applyEffective();
        }

        function getPreference() {
            return { ...state };
        }

        // Listen for OS theme changes when pref is 'auto'.
        if (window.matchMedia) {
            const mq = window.matchMedia("(prefers-color-scheme: dark)");
            const onChange = () => {
                if (state.mode === "auto") {
                    applyEffective();
                }
            };
            if (mq.addEventListener) {
                mq.addEventListener("change", onChange);
            } else if (mq.addListener) {
                mq.addListener(onChange);
            }
        }

        // Hydrate from server asynchronously; don't block startup.
        loadFromUser();

        return {
            getPreference,
            setPreference,
            applyEffective,
        };
    },
};

registry.category("services").add("ldDarkMode", ldDarkModeService);
