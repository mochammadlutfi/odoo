/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { getReportUrl } from "@web/webclient/actions/reports/utils";
import { PDFPreviewDialog } from "./pdf_preview_dialog";

// Cache status wkhtmltopdf — sama persis dengan cara Odoo sendiri melakukannya
let _wkhtmltopdfStatusProm = null;

function checkWkhtmltopdf() {
    _wkhtmltopdfStatusProm ||= rpc("/report/check_wkhtmltopdf");
    return _wkhtmltopdfStatusProm;
}

/**
 * Register handler di "ir.actions.report handlers" registry.
 * Odoo 18 action_service iterates handlers SEBELUM default download behavior.
 * Return truthy = stop processing. Return falsy = lanjut ke handler berikutnya.
 *
 * Guard: cek wkhtmltopdf dulu. Kalau tidak tersedia → return false
 * supaya Odoo fallback ke HTML renderer seperti biasa.
 */
registry.category("ir.actions.report handlers").add("ld_pdf_preview_pro", async (action, options, env) => {
    if (action.report_type !== "qweb-pdf") {
        return false;
    }

    const status = await checkWkhtmltopdf();
    if (!["ok", "upgrade"].includes(status)) {
        // wkhtmltopdf tidak tersedia — biarkan Odoo fallback ke HTML
        return false;
    }

    const pdfUrl = getReportUrl(action, "pdf");
    const title = action.display_name || action.name || "Report";

    env.services.dialog.add(PDFPreviewDialog, {
        pdfUrl,
        downloadUrl: pdfUrl,
        title,
    });

    return true;
});
