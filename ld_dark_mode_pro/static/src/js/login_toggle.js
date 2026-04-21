/** @odoo-module **/

/**
 * Non-OWL widget: injects a tiny sun/moon button in the top-right of login,
 * signup, and other public /web/login-style pages. Click cycles
 * light → dark → auto → light. Writes to localStorage only; the inline head
 * script picks up the change and (when needed) reloads once.
 */

const LOCAL_KEY = "ldDarkMode";
const BUTTON_ID = "ld_dm_login_toggle";
const RELOAD_FLAG = "ldDarkReloaded";
const CYCLE = ["light", "dark", "auto"];

function isLoginPage() {
    const p = window.location.pathname;
    return (
        p === "/web/login" ||
        p === "/web/signup" ||
        p === "/web/reset_password" ||
        p.startsWith("/web/login/")
    );
}

function readState() {
    try {
        const raw = window.localStorage.getItem(LOCAL_KEY);
        return raw ? JSON.parse(raw) : { mode: "auto", scheduleStart: 19, scheduleEnd: 7 };
    } catch (_) {
        return { mode: "auto", scheduleStart: 19, scheduleEnd: 7 };
    }
}

function writeState(state) {
    try {
        window.localStorage.setItem(LOCAL_KEY, JSON.stringify(state));
    } catch (_) {
        // Ignore private-mode storage errors.
    }
}

function setCookie(mode) {
    const oneYear = 60 * 60 * 24 * 365;
    const secureFlag = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie =
        "color_scheme=" + mode +
        "; path=/; max-age=" + oneYear + "; SameSite=Lax" + secureFlag;
}

function ensureButton() {
    if (!isLoginPage() || document.getElementById(BUTTON_ID)) {
        return;
    }
    const btn = document.createElement("button");
    btn.id = BUTTON_ID;
    btn.type = "button";
    btn.setAttribute("aria-label", "Toggle dark mode");
    btn.className = "ld_dm_login_toggle";
    btn.style.cssText = [
        "position:fixed", "top:12px", "right:16px", "z-index:9999",
        "background:transparent", "border:1px solid currentColor",
        "border-radius:999px", "width:36px", "height:36px",
        "cursor:pointer", "font-size:16px",
        "display:inline-flex", "align-items:center", "justify-content:center",
    ].join(";");

    const update = () => {
        const state = readState();
        const icons = { light: "\u2600", dark: "\u263D", auto: "A" };
        btn.textContent = icons[state.mode] || icons.auto;
        btn.title = "Dark Mode: " + state.mode;
    };

    btn.addEventListener("click", () => {
        const state = readState();
        const idx = CYCLE.indexOf(state.mode);
        const next = CYCLE[(idx + 1) % CYCLE.length];
        const updated = { ...state, mode: next };
        writeState(updated);

        // Resolve effective cookie & reload once so the correct asset bundle
        // is served. The inline head script's reload-guard prevents loops.
        let effective;
        if (next === "dark") {
            effective = "dark";
        } else if (next === "light") {
            effective = "light";
        } else {
            const mq = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
            effective = mq && mq.matches ? "dark" : "light";
        }
        setCookie(effective);
        try {
            window.sessionStorage.removeItem(RELOAD_FLAG);
        } catch (_) {}
        window.location.reload();
        update();
    });

    update();
    document.body.appendChild(btn);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureButton);
} else {
    ensureButton();
}
