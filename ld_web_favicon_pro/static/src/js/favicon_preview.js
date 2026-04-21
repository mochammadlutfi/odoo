/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * FaviconPreview — shows live preview of generated favicon sizes.
 * Registered as a field widget (widget="favicon_preview") on a Binary field.
 */
export class FaviconPreviewWidget extends Component {
    static template = "ld_web_favicon_pro.FaviconPreview";

    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            loading: false,
            error: null,
            previews: {},
        });

        onWillStart(() => this._loadPreview());
    }

    get companyId() {
        return this.props.record?.resId || false;
    }

    async _loadPreview() {
        const id = this.companyId;
        if (!id) {
            return;
        }

        this.state.loading = true;
        this.state.error = null;

        try {
            const result = await this.rpc("/ld_favicon/preview", {
                company_id: id,
            });

            if (result && result.error) {
                this.state.error = result.error;
                this.state.previews = {};
            } else if (result && result.previews) {
                this.state.previews = result.previews;
            }
        } catch (e) {
            this.state.error = "Gagal load preview. Pastikan company logo sudah di-set.";
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("fields").add("favicon_preview", {
    component: FaviconPreviewWidget,
    displayName: "Favicon Preview",
    supportedTypes: ["binary"],
});
