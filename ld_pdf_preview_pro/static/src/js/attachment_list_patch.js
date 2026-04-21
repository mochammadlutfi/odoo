/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { url } from "@web/core/utils/urls";
import { AttachmentList } from "@mail/core/common/attachment_list";
import { PDFPreviewDialog } from "./pdf_preview_dialog";

/**
 * Intercept PDF attachment clicks di chatter/message thread.
 * Buka PDFPreviewDialog via PDF.js alih-alih default FileViewer (iframe viewer.html).
 */
patch(AttachmentList.prototype, {
    setup() {
        super.setup();
        const _originalOpen = this.fileViewer.open.bind(this.fileViewer);
        this.fileViewer.open = (file, files) => {
            if (file.isPdf) {
                this.dialog.add(PDFPreviewDialog, {
                    pdfUrl: url(file.urlRoute, file.urlQueryParams),
                    downloadUrl: file.downloadUrl,
                    title: file.displayName,
                });
                return;
            }
            return _originalOpen(file, files);
        };
    },
});
