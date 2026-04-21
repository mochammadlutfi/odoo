/** @odoo-module **/

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";

/**
 * Quick Search service — owns RPC + localStorage cache for recent searches.
 *
 * Recents are persisted server-side (per user) AND mirrored to localStorage
 * so the palette opens instantly even on first keystroke.
 */
export const quickSearchService = {
    dependencies: ["rpc", "orm", "action", "notification"],

    start(env, { rpc, orm, action, notification }) {
        const STORAGE_KEY = "ld_quick_search.recents.v1";
        const MAX_LOCAL_RECENTS = 10;

        /**
         * @param {string} query
         * @param {string} scope   "menu" | "action" | "record"
         * @param {string|null} [model]
         * @returns {Promise<Array<Object>>}
         */
        async function search(query, scope, model = null) {
            try {
                const payload = { query, scope };
                if (model) payload.model = model;
                const res = await rpc("/ld_quick_search/search", payload);
                return (res && res.results) || [];
            } catch (err) {
                notification.add(_t("Quick search failed"), { type: "danger" });
                // eslint-disable-next-line no-console
                if (env.debug) console.warn("quick_search rpc", err);
                return [];
            }
        }

        function loadLocalRecents() {
            try {
                const raw = browser.localStorage.getItem(STORAGE_KEY);
                if (!raw) return [];
                const parsed = JSON.parse(raw);
                return Array.isArray(parsed) ? parsed.slice(0, MAX_LOCAL_RECENTS) : [];
            } catch {
                return [];
            }
        }

        function saveLocalRecents(items) {
            try {
                browser.localStorage.setItem(
                    STORAGE_KEY,
                    JSON.stringify(items.slice(0, MAX_LOCAL_RECENTS))
                );
            } catch {
                /* storage full / disabled — ignore */
            }
        }

        function pushRecent(item) {
            const recents = loadLocalRecents();
            const key = JSON.stringify([item.type, item.id, item.model || ""]);
            const filtered = recents.filter(
                (r) => JSON.stringify([r.type, r.id, r.model || ""]) !== key
            );
            filtered.unshift({ ...item, _ts: Date.now() });
            saveLocalRecents(filtered);

            // Fire-and-forget server mirror — do not block navigation.
            rpc("/ld_quick_search/record_usage", {
                action_id: item.action_id || false,
                res_model: item.model || item.res_model || false,
                res_id: item.id || false,
                query: item.label || false,
            }).catch(() => {});
        }

        async function openResult(result) {
            pushRecent(result);
            if (result.type === "menu" || result.type === "action") {
                if (result.action_id) {
                    await action.doAction(result.action_id);
                    return;
                }
                if (result.id && result.type === "action") {
                    await action.doAction(result.id);
                    return;
                }
            }
            if (result.type === "record" && result.model) {
                await action.doAction({
                    type: "ir.actions.act_window",
                    res_model: result.model,
                    res_id: result.id,
                    views: [[false, "form"]],
                    target: "current",
                });
                return;
            }
            if (result.type === "favorite") {
                if (result.action_id) {
                    await action.doAction(result.action_id);
                } else if (result.res_model && result.res_id) {
                    await action.doAction({
                        type: "ir.actions.act_window",
                        res_model: result.res_model,
                        res_id: result.res_id,
                        views: [[false, "form"]],
                        target: "current",
                    });
                }
                return;
            }
        }

        async function fetchRecents() {
            try {
                const res = await rpc("/ld_quick_search/recents", {});
                return (res && res.results) || [];
            } catch {
                return loadLocalRecents();
            }
        }

        async function fetchFavorites() {
            try {
                const res = await rpc("/ld_quick_search/favorites", {});
                return (res && res.results) || [];
            } catch {
                return [];
            }
        }

        return {
            search,
            openResult,
            pushRecent,
            fetchRecents,
            fetchFavorites,
            loadLocalRecents,
        };
    },
};

registry.category("services").add("quick_search", quickSearchService);
