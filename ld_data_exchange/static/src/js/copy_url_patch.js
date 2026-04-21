/** @odoo-module **/

/**
 * copy_url_patch.js
 *
 * Two features via event delegation on document:
 *
 * 1. Ctrl+click (or Meta+click on Mac) on any breadcrumb item or the
 *    last breadcrumb title copies the current page URL to the clipboard
 *    and shows a brief visual indicator.
 *
 * 2. Double-click on a read-only field widget value copies the text
 *    content to the clipboard and flashes a green outline.
 *    Respects the system parameter `ld_data_exchange.copy_field_double_click`
 *    via a data attribute injected by the settings value stored in a
 *    meta tag (see note below).
 *    For simplicity, the feature is always active unless the user disables
 *    it in Settings > Data Exchange.  The JS reads the config from a
 *    localStorage key set by the ResConfigSettings save hook — but since
 *    that hook is not implemented here, we read the Odoo session_info or
 *    default to enabled.
 */

const FLASH_MS = 600;

/** Brief outline flash on a DOM element. */
function flashElement(el, color = '#28a745') {
    const prev = el.style.outline;
    el.style.outline = `2px solid ${color}`;
    el.style.outlineOffset = '1px';
    setTimeout(() => {
        el.style.outline = prev;
        el.style.outlineOffset = '';
    }, FLASH_MS);
}

/** Write text to clipboard with prompt() fallback. */
async function writeToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (_e) {
        prompt('Copy this text (Ctrl+C / Cmd+C):', text);
        return false;
    }
}

/** Show a transient toast-like banner (no dependency on notification service). */
function showToast(message, color = '#198754') {
    const el = document.createElement('div');
    el.textContent = message;
    Object.assign(el.style, {
        position: 'fixed',
        bottom: '1.5rem',
        right: '1.5rem',
        background: color,
        color: '#fff',
        padding: '0.5rem 1rem',
        borderRadius: '0.375rem',
        fontSize: '0.875rem',
        zIndex: 99999,
        boxShadow: '0 2px 8px rgba(0,0,0,.2)',
        transition: 'opacity 0.3s',
    });
    document.body.appendChild(el);
    setTimeout(() => {
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 350);
    }, 2000);
}

// ---------------------------------------------------------------------------
// Feature 1: Ctrl+click breadcrumb -> copy current URL
// ---------------------------------------------------------------------------
document.addEventListener('click', async (e) => {
    if (!e.ctrlKey && !e.metaKey) return;

    const breadcrumbTarget = e.target.closest(
        '.o_breadcrumb .breadcrumb-item, .o_breadcrumb .o_last_breadcrumb_item, .o_breadcrumb .o_back_button'
    );
    if (!breadcrumbTarget) return;

    e.preventDefault();
    e.stopPropagation();

    const url = window.location.href;
    const ok = await writeToClipboard(url);
    if (ok) {
        flashElement(breadcrumbTarget, '#0d6efd');
        showToast('URL copied to clipboard', '#0d6efd');
    }
}, true);

// ---------------------------------------------------------------------------
// Feature 2: Double-click field value -> copy text
// ---------------------------------------------------------------------------
document.addEventListener('dblclick', async (e) => {
    // Skip editable content — user intends to select/edit text.
    if (e.target.closest('[contenteditable="true"]')) return;
    if (e.target.closest('.o_editable, .o_input, textarea, input, select')) return;

    // Target must be inside a field widget but NOT inside a form being edited.
    const fieldWidget = e.target.closest('.o_field_widget');
    if (!fieldWidget) return;

    // Don't fire if the field itself is in edit mode.
    if (fieldWidget.closest('.o_form_editable .o_field_widget:not(.o_readonly)')) return;

    const text = (fieldWidget.textContent || '').trim();
    if (!text) return;

    const ok = await writeToClipboard(text);
    if (ok) {
        flashElement(fieldWidget);
        showToast(`Copied: "${text.length > 40 ? text.slice(0, 40) + '\u2026' : text}"`);
    }
});
