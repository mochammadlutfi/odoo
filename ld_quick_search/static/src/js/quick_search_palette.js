/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { fuzzyRank, highlightSpans } from "./fuzzy";

const DEBOUNCE_MS = 150;

function isMac() {
    const nav = browser.navigator || {};
    const ua = nav.userAgentData?.platform || nav.platform || nav.userAgent || "";
    return /Mac|iPhone|iPad|iPod/i.test(ua);
}

/**
 * Parse the raw input into { scope, model, query }.
 *
 *   ""             → { scope: "menu",   model: null, query: "" }
 *   "sales"        → { scope: "menu",   model: null, query: "sales" }
 *   "> new sale"   → { scope: "action", model: null, query: "new sale" }
 *   "#users"       → { scope: "menu",   model: null, query: "users" }   // settings live as menu
 *   "@partner joe" → { scope: "record", model: "res.partner", query: "joe" }
 *
 * @param {string} raw
 */
export function parseInput(raw) {
    const s = (raw || "").trim();
    if (!s) return { scope: "menu", model: null, query: "" };
    if (s.startsWith(">")) {
        return { scope: "action", model: null, query: s.slice(1).trim() };
    }
    if (s.startsWith("#")) {
        return { scope: "menu", model: null, query: s.slice(1).trim() };
    }
    if (s.startsWith("@")) {
        const rest = s.slice(1).trim();
        const sp = rest.indexOf(" ");
        if (sp === -1) {
            return { scope: "record", model: rest, query: "" };
        }
        return {
            scope: "record",
            model: rest.slice(0, sp).trim(),
            query: rest.slice(sp + 1).trim(),
        };
    }
    return { scope: "menu", model: null, query: s };
}

/**
 * Resolve shortcut string like "ctrl+k" against a KeyboardEvent.
 * On macOS, "ctrl+k" maps to Cmd+K automatically.
 *
 * @param {string} shortcut
 * @param {KeyboardEvent} ev
 */
export function matchShortcut(shortcut, ev, opts = {}) {
    const parts = (shortcut || "ctrl+k").toLowerCase().split("+").map((p) => p.trim());
    if (!parts.length) return false;
    const key = parts[parts.length - 1];
    const mods = new Set(parts.slice(0, -1));
    const mac = typeof opts.mac === "boolean" ? opts.mac : isMac();

    const wantsCtrl = mods.has("ctrl");
    const wantsMeta = mods.has("meta");
    const wantsShift = mods.has("shift");
    const wantsAlt = mods.has("alt");

    // On Mac, "ctrl" in the config means "the primary modifier" which is Cmd.
    // We translate wantsCtrl → wantsMeta on Mac, and require the other modifier
    // to be NOT pressed so `ctrl+k` does not also fire on literal Ctrl+K.
    let needCtrl, needMeta;
    if (mac && wantsCtrl && !wantsMeta) {
        needCtrl = false;
        needMeta = true;
    } else {
        needCtrl = wantsCtrl;
        needMeta = wantsMeta;
    }

    return (
        (ev.key || "").toLowerCase() === key &&
        ev.ctrlKey === needCtrl &&
        ev.metaKey === needMeta &&
        ev.shiftKey === wantsShift &&
        ev.altKey === wantsAlt
    );
}

export class QuickSearchPalette extends Component {
    static template = "ld_quick_search.Palette";
    static props = {};

    setup() {
        this.quickSearch = useService("quick_search");
        this.inputRef = useRef("input");

        this.state = useState({
            open: false,
            input: "",
            results: [],
            selectedIndex: 0,
            loading: false,
            emptyHint: "",
        });

        this._debounceTimer = null;
        this._requestSeq = 0;
        this._onKeyDown = this._onKeyDown.bind(this);

        // Shortcut: read from session if available; otherwise default.
        this._shortcut = (
            (this.env.session && this.env.session.ld_quick_search_shortcut) ||
            "ctrl+k"
        );

        onMounted(() => {
            document.addEventListener("keydown", this._onKeyDown, true);
        });
        onWillUnmount(() => {
            document.removeEventListener("keydown", this._onKeyDown, true);
            if (this._debounceTimer) clearTimeout(this._debounceTimer);
        });
    }

    _onKeyDown(ev) {
        if (!this.state.open && matchShortcut(this._shortcut, ev)) {
            ev.preventDefault();
            ev.stopPropagation();
            this.open();
            return;
        }
        if (!this.state.open) return;

        if (ev.key === "Escape") {
            ev.preventDefault();
            this.close();
            return;
        }
        if (ev.key === "ArrowDown") {
            ev.preventDefault();
            this._moveSelection(1);
            return;
        }
        if (ev.key === "ArrowUp") {
            ev.preventDefault();
            this._moveSelection(-1);
            return;
        }
        if (ev.key === "Enter") {
            ev.preventDefault();
            this._openSelected();
        }
    }

    _moveSelection(delta) {
        const n = this.state.results.length;
        if (n === 0) return;
        this.state.selectedIndex = (this.state.selectedIndex + delta + n) % n;
    }

    async open() {
        this.state.open = true;
        this.state.input = "";
        this.state.results = [];
        this.state.selectedIndex = 0;
        this._preloadSeq = (this._preloadSeq || 0) + 1;
        this._showPreload().catch((err) => {
            // eslint-disable-next-line no-console
            if (this.env.debug) console.warn("quick_search preload", err);
        });
        // Focus after next paint.
        Promise.resolve().then(() => {
            if (this.inputRef.el) this.inputRef.el.focus();
        });
    }

    close() {
        this.state.open = false;
        this.state.input = "";
        this.state.results = [];
        this.state.selectedIndex = 0;
        if (this._debounceTimer) {
            clearTimeout(this._debounceTimer);
            this._debounceTimer = null;
        }
    }

    async _showPreload() {
        const mySeq = this._preloadSeq;
        const [recents, favorites] = await Promise.all([
            this.quickSearch.fetchRecents(),
            this.quickSearch.fetchFavorites(),
        ]);
        // User may have closed or re-opened the palette while awaiting.
        if (!this.state.open || mySeq !== this._preloadSeq) return;
        const items = [
            ...favorites.map((f) => ({ ...f, _group: "Favorites" })),
            ...recents.map((r) => ({ ...r, _group: "Recent" })),
        ];
        this.state.results = items;
        this.state.selectedIndex = 0;
        this.state.emptyHint = items.length
            ? ""
            : _t("Type to search menus. Try '> action', '#setting', '@model query'.");
    }

    onInput(ev) {
        const value = ev.target.value;
        this.state.input = value;
        if (this._debounceTimer) clearTimeout(this._debounceTimer);
        this._debounceTimer = setTimeout(() => this._runSearch(value), DEBOUNCE_MS);
    }

    async _runSearch(raw) {
        const parsed = parseInput(raw);
        if (!raw.trim()) {
            this._preloadSeq = (this._preloadSeq || 0) + 1;
            await this._showPreload();
            return;
        }
        this.state.loading = true;
        const mySeq = ++this._requestSeq;
        let results = [];
        try {
            results = await this.quickSearch.search(
                parsed.query,
                parsed.scope,
                parsed.model
            );
        } finally {
            // Only the winning request clears the spinner; stale ones just return.
            if (mySeq === this._requestSeq) {
                this.state.loading = false;
            }
        }
        if (mySeq !== this._requestSeq) return; // stale
        if (!this.state.open) return;           // palette closed while awaiting

        let ranked;
        if (parsed.scope === "menu" && parsed.query) {
            ranked = fuzzyRank(parsed.query, results, { keys: ["label", "path"], limit: 30 });
        } else {
            ranked = results.map((r) => ({ item: r, score: 0, indices: [], key: "label" }));
        }

        this.state.results = ranked.map(({ item, indices, key }) => ({
            ...item,
            _spans: highlightSpans(item[key] || item.label || "", indices || []),
        }));
        this.state.selectedIndex = 0;
        this.state.emptyHint = this.state.results.length
            ? ""
            : _t("No results. Try '@model' for records, '>' for actions.");
    }

    onResultClick(idx) {
        this.state.selectedIndex = idx;
        this._openSelected();
    }

    async _openSelected() {
        const item = this.state.results[this.state.selectedIndex];
        if (!item) return;
        this.close();
        await this.quickSearch.openResult(item);
    }

    onBackdropClick(ev) {
        if (ev.target.classList.contains("o_qs_backdrop")) {
            this.close();
        }
    }

    /** Stable key for t-foreach — falls back to index only when id is missing. */
    resultKey(r, index) {
        const id = r.id ?? r.res_id ?? "";
        const model = r.model || r.res_model || "";
        return `${r.type || "?"}|${model}|${id || `i${index}`}`;
    }
}

registry.category("main_components").add("QuickSearchPalette", {
    Component: QuickSearchPalette,
});
