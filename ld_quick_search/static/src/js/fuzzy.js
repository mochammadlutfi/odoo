/** @odoo-module **/

/**
 * Lightweight fuzzy matcher — subsequence + contiguous bonus.
 *
 * Score components:
 *   - +1    per matched char
 *   - +4    if match starts at string boundary (start or after space / "/")
 *   - +2    per contiguous run of 2+ matched chars
 *   - -0.5  per skipped char between matches
 *
 * Returns { score, indices } or null if no match.
 *
 * @param {string} pattern   user query (case-insensitive)
 * @param {string} text      candidate text
 * @returns {{score: number, indices: number[]} | null}
 */
export function fuzzyMatch(pattern, text) {
    if (!pattern) {
        return { score: 0, indices: [] };
    }
    if (!text) {
        return null;
    }
    const p = pattern.toLowerCase();
    const t = text.toLowerCase();

    const indices = [];
    let ti = 0;
    let pi = 0;
    let score = 0;
    let runLength = 0;
    let lastMatch = -1;

    while (pi < p.length && ti < t.length) {
        if (p[pi] === t[ti]) {
            indices.push(ti);
            score += 1;
            // Boundary bonus.
            if (ti === 0 || /[\s/._-]/.test(t[ti - 1])) {
                score += 4;
            }
            // Contiguous run bonus — only reward runs of 2+ matched chars.
            if (lastMatch === ti - 1) {
                runLength += 1;
                if (runLength >= 2) {
                    score += 2;
                }
            } else {
                runLength = 1;
                if (lastMatch >= 0) {
                    score -= 0.5 * (ti - lastMatch - 1);
                }
            }
            lastMatch = ti;
            pi += 1;
        }
        ti += 1;
    }

    if (pi !== p.length) {
        return null;
    }
    return { score, indices };
}

/**
 * Rank candidates by fuzzy score against pattern. Stable for ties.
 *
 * @param {string} pattern
 * @param {Array<{label: string}>} candidates
 * @param {{keys?: string[], limit?: number}} [opts]
 * @returns {Array<{item: Object, score: number, indices: number[], key: string}>}
 */
export function fuzzyRank(pattern, candidates, opts = {}) {
    const keys = opts.keys || ["label"];
    const limit = opts.limit || 50;
    const scored = [];
    for (const item of candidates) {
        let best = null;
        let bestKey = keys[0];
        for (const key of keys) {
            const value = item[key];
            if (typeof value !== "string") continue;
            const m = fuzzyMatch(pattern, value);
            if (m && (!best || m.score > best.score)) {
                best = m;
                bestKey = key;
            }
        }
        if (best) {
            scored.push({ item, score: best.score, indices: best.indices, key: bestKey });
        }
    }
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, limit);
}

/**
 * Build an array of {type, value} spans that mark which chars in `text`
 * were matched, for highlighting.
 *
 * @param {string} text
 * @param {number[]} indices
 * @returns {Array<{match: boolean, value: string}>}
 */
export function highlightSpans(text, indices) {
    if (!text) return [];
    if (!indices || !indices.length) return [{ match: false, value: text }];
    const set = new Set(indices);
    const spans = [];
    let buf = "";
    let bufMatch = set.has(0);
    for (let i = 0; i < text.length; i += 1) {
        const m = set.has(i);
        if (m === bufMatch) {
            buf += text[i];
        } else {
            if (buf) spans.push({ match: bufMatch, value: buf });
            buf = text[i];
            bufMatch = m;
        }
    }
    if (buf) spans.push({ match: bufMatch, value: buf });
    return spans;
}
