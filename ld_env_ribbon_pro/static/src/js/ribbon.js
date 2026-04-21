/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

class EnvironmentRibbon extends Component {
    static template = "ld_env_ribbon_pro.Ribbon";
    static props = {};

    setup() {
        this.config = session.ribbon_config || { enabled: false };
        this.state = useState({ dismissed: false });
        this._checkDismissed();
    }

    _checkDismissed() {
        if (!this.config.user_dismissable) return;
        const key = `ribbon_dismissed_${new Date().toDateString()}`;
        this.state.dismissed = localStorage.getItem(key) === "true";
    }

    dismiss() {
        const key = `ribbon_dismissed_${new Date().toDateString()}`;
        localStorage.setItem(key, "true");
        this.state.dismissed = true;
    }

    get ribbonClasses() {
        const { style = "bar", position = "top_right", environment = "" } = this.config;
        return [
            "env-ribbon",
            `env-ribbon-style-${style}`,
            `env-ribbon-pos-${position}`,
            environment ? `env-ribbon-env-${environment}` : "",
        ]
            .filter(Boolean)
            .join(" ");
    }

    get ribbonStyle() {
        return this.config.color ? `background-color: ${this.config.color};` : "";
    }
}

registry.category("main_components").add("EnvironmentRibbon", {
    Component: EnvironmentRibbon,
});
