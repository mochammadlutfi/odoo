/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { STATIC_ACTIONS_GROUP_NUMBER } from "@web/search/action_menus/action_menus";
import { Component } from "@odoo/owl";

const cogMenuRegistry = registry.category("cogMenu");

/**
 * CopyListMenu
 *
 * Adds Copy as TSV/CSV/Markdown/JSON items to the list view cog menu.
 * Copies all visible rows, or only selected rows if any are checked.
 */
export class CopyListMenu extends Component {
    static template = "ld_data_exchange.CopyListMenu";
    static components = { DropdownItem };
    static props = {};

    setup() {
        this.notification = useService("notification");
    }

    /**
     * Builds a flat string value from a record field.
     * Many2one fields have {id, display_name}; booleans show as empty string.
     */
    _fieldValue(val) {
        if (val === false || val === undefined || val === null) return '';
        if (typeof val === 'object' && val.display_name !== undefined) return val.display_name;
        return String(val);
    }

    async copyToClipboard(format) {
        const model = this.env.model;
        const root = model.root;

        // Columns: only type==='field' entries carry data
        const columns = (this.env.config.viewArch
            ? Array.from(this.env.config.viewArch.querySelectorAll('field')).map(el => ({
                name: el.getAttribute('name'),
                string: el.getAttribute('string') || el.getAttribute('name'),
              }))
            : []
        );

        // Fallback: derive columns from archInfo if viewArch query returns nothing
        const archColumns = this.env.config.archInfo?.columns
            ? this.env.config.archInfo.columns.filter(c => c.type === 'field')
            : [];

        const cols = columns.length ? columns : archColumns.map(c => ({
            name: c.name,
            string: c.string || c.label || c.name,
        }));

        // Records: prefer selection, fall back to all loaded records
        const allRecords = root.records || [];
        const selected = allRecords.filter(r => r.selected);
        const targets = selected.length ? selected : allRecords;

        if (!targets.length) {
            this.notification.add('No records to copy.', { type: 'warning', sticky: false });
            return;
        }

        const headers = cols.map(c => c.string);
        const rows = targets.map(rec =>
            cols.map(c => this._fieldValue(rec.data[c.name]))
        );

        let text = '';
        if (format === 'tsv') {
            text = [headers, ...rows].map(r => r.join('\t')).join('\n');
        } else if (format === 'csv') {
            const esc = v => `"${String(v).replace(/"/g, '""')}"`;
            text = [headers, ...rows].map(r => r.map(esc).join(',')).join('\n');
        } else if (format === 'markdown') {
            const hr = headers.map(() => '---');
            text = [
                `| ${headers.join(' | ')} |`,
                `| ${hr.join(' | ')} |`,
                ...rows.map(r => `| ${r.join(' | ')} |`),
            ].join('\n');
        } else if (format === 'json') {
            const data = targets.map(rec => {
                const obj = {};
                cols.forEach(c => { obj[c.name] = rec.data[c.name] ?? null; });
                return obj;
            });
            text = JSON.stringify(data, null, 2);
        }

        try {
            await navigator.clipboard.writeText(text);
        } catch (_e) {
            // Fallback for browsers/contexts that block clipboard API
            prompt('Copy this text (Ctrl+C / Cmd+C):', text);
            return;
        }

        this.notification.add(
            `Copied ${targets.length} row(s) as ${format.toUpperCase()}`,
            { type: 'success', sticky: false }
        );
    }
}

export const copyListMenuItem = {
    Component: CopyListMenu,
    groupNumber: STATIC_ACTIONS_GROUP_NUMBER,
    isDisplayed: (env) => env.config.viewType === 'list',
};

cogMenuRegistry.add('ld-copy-list-menu', copyListMenuItem, { sequence: 20 });
