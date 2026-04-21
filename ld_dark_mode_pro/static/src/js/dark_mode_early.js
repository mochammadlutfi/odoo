/** @odoo-module **/

/**
 * Frontend (public-facing) early script. Runs inside `web.assets_frontend`
 * after the inline head script has already applied first-paint styling.
 *
 * Purpose: keep the `data-ld-dark` attribute and `color_scheme` cookie in
 * sync on navigation / bfcache restores — scenarios where the inline head
 * script does not re-execute.
 */

const LOCAL_KEY = "ldDarkMode";

const VALID = new Set(["light", "dark", "auto", "schedule"]);

function _clampHour(v, fallback) {
    if (typeof v !== "number" || Number.isNaN(v) || v < 0 || v >= 24) {
        return fallback;
    }
    return v;
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

function _isWithinSchedule(now, start, end) {
    if (start === end) {
        return false;
    }
    if (start < end) {
        return now >= start && now < end;
    }
    return now >= start || now < end;
}

function _effective(state) {
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

function applyOnce() {
    const state = _readLocal();
    const effective = _effective(state);
    if (effective === "dark") {
        document.documentElement.setAttribute("data-ld-dark", "1");
    } else {
        document.documentElement.removeAttribute("data-ld-dark");
    }
}

window.addEventListener("pageshow", applyOnce);
applyOnce();
