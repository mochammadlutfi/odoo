/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { isMobileOS } from "@web/core/browser/feature_detection";
import { loadPDFJSAssets } from "@web/libs/pdfjs";

const PDFJS_WORKER = "/web/static/lib/pdfjs/build/pdf.worker.js";

async function loadPdfJs() {
    await loadPDFJSAssets();
    globalThis.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_WORKER;
    return globalThis.pdfjsLib;
}

export class PDFPreviewDialog extends Component {
    static template = "ld_pdf_preview_pro.PDFPreviewDialog";
    static components = { Dialog };
    static props = {
        pdfUrl: String,
        downloadUrl: String,
        title: String,
        close: Function,
    };

    setup() {
        this.canvasRef = useRef("pdfCanvas");
        this.bodyRef = useRef("pdfBody");
        this.isMobile = isMobileOS();
        this._touchStartX = 0;
        this._pdf = null;
        this._darkQuery = null;
        this._onDarkChange = null;

        this.state = useState({
            currentPage: 1,
            totalPages: 0,
            scale: 1.0,
            loading: true,
            error: null,
            rendering: false,
            darkMode: window.matchMedia("(prefers-color-scheme: dark)").matches,
        });

        onMounted(async () => {
            await this._loadPDF();
            this._setupSwipe();
            this._darkQuery = window.matchMedia("(prefers-color-scheme: dark)");
            this._onDarkChange = (e) => {
                this.state.darkMode = e.matches;
            };
            this._darkQuery.addEventListener("change", this._onDarkChange);
        });

        onWillUnmount(() => {
            this._darkQuery?.removeEventListener("change", this._onDarkChange);
            this._pdf?.destroy();
        });
    }

    get pageLabel() {
        return `${this.state.currentPage} / ${this.state.totalPages}`;
    }

    get zoomLabel() {
        return Math.round(this.state.scale * 100) + "%";
    }

    async _loadPDF() {
        try {
            const pdfjsLib = await loadPdfJs();
            this._pdf = await pdfjsLib.getDocument(this.props.pdfUrl).promise;
            this.state.totalPages = this._pdf.numPages;
            this.state.loading = false;
            // Poll until OWL mounts the canvas after state change
            await new Promise((resolve) => {
                const check = () => (this.canvasRef.el ? resolve() : requestAnimationFrame(check));
                requestAnimationFrame(check);
            });
            await this._renderPage(1);
        } catch {
            this.state.error = _t("Gagal memuat PDF. Silakan coba lagi.");
            this.state.loading = false;
        }
    }

    async _renderPage(num) {
        if (!this._pdf || this.state.rendering) return;
        this.state.rendering = true;
        try {
            const page = await this._pdf.getPage(num);
            const canvas = this.canvasRef.el;
            if (!canvas) return;

            // Use body scroll container width minus horizontal padding (2 × 24px)
            const bodyEl = this.bodyRef.el;
            const availableWidth = (bodyEl?.clientWidth || 800) - 48;
            const naturalViewport = page.getViewport({ scale: 1 });
            const baseScale = availableWidth / naturalViewport.width;
            const scale = baseScale * this.state.scale;

            const dpr = window.devicePixelRatio || 1;
            const viewport = page.getViewport({ scale: scale * dpr });
            canvas.width = Math.floor(viewport.width);
            canvas.height = Math.floor(viewport.height);
            canvas.style.width = Math.floor(viewport.width / dpr) + "px";
            canvas.style.height = Math.floor(viewport.height / dpr) + "px";

            const ctx = canvas.getContext("2d");
            await page.render({ canvasContext: ctx, viewport }).promise;
            this.state.currentPage = num;

            // Scroll to top of body after page change
            if (bodyEl) bodyEl.scrollTop = 0;
        } finally {
            this.state.rendering = false;
        }
    }

    async nextPage() {
        if (this.state.currentPage < this.state.totalPages && !this.state.rendering) {
            await this._renderPage(this.state.currentPage + 1);
        }
    }

    async prevPage() {
        if (this.state.currentPage > 1 && !this.state.rendering) {
            await this._renderPage(this.state.currentPage - 1);
        }
    }

    async zoomIn() {
        if (this.state.scale >= 3.0) return;
        this.state.scale = Math.min(this.state.scale + 0.25, 3.0);
        await this._renderPage(this.state.currentPage);
    }

    async zoomOut() {
        if (this.state.scale <= 0.25) return;
        this.state.scale = Math.max(this.state.scale - 0.25, 0.25);
        await this._renderPage(this.state.currentPage);
    }

    printPDF() {
        const iframe = document.createElement("iframe");
        iframe.style.cssText =
            "position:fixed;top:-9999px;left:-9999px;width:1px;height:1px;border:none;";
        iframe.src = this.props.pdfUrl;
        document.body.appendChild(iframe);
        iframe.onload = () => {
            try {
                iframe.contentWindow.focus();
                iframe.contentWindow.print();
            } catch {
                window.open(this.props.pdfUrl, "_blank");
            }
            setTimeout(() => document.body.removeChild(iframe), 3000);
        };
    }

    _setupSwipe() {
        const el = this.bodyRef.el;
        if (!el || !this.isMobile) return;
        el.addEventListener(
            "touchstart",
            (e) => {
                this._touchStartX = e.changedTouches[0].screenX;
            },
            { passive: true }
        );
        el.addEventListener(
            "touchend",
            (e) => {
                const diff = this._touchStartX - e.changedTouches[0].screenX;
                if (Math.abs(diff) > 50) {
                    diff > 0 ? this.nextPage() : this.prevPage();
                }
            },
            { passive: true }
        );
    }
}
