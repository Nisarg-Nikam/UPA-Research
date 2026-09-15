(() => {
    "use strict";

    const SELECTOR = [
        ".research-card h2",
        ".domain-card h2",
        ".record-card h2",
        ".patent-card h2",
        ".card h2"
    ].join(",");

    function fitHeading(el) {
        if (!el || !el.isConnected) return;

        el.classList.add("upa-fit-heading");

        const computed = getComputedStyle(el);
        const originalSize = parseFloat(computed.fontSize) || 32;
        const originalWeight = computed.fontWeight;
        const maxLines = 3;

        el.style.fontSize = "";
        el.style.lineHeight = "";
        el.style.height = "";
        el.style.maxHeight = "";

        const lineHeight = parseFloat(getComputedStyle(el).lineHeight);
        const safeLineHeight = Number.isFinite(lineHeight) ? lineHeight : originalSize * 1.1;

        const fits = () => {
            const height = el.getBoundingClientRect().height;
            return height <= (safeLineHeight * maxLines + 3);
        };

        let low = 16;
        let high = Math.max(18, originalSize);
        let best = low;

        while (low <= high) {
            const mid = (low + high) / 2;
            el.style.fontSize = `${mid}px`;
            el.style.lineHeight = `${Math.max(1.05, Math.min(1.12, safeLineHeight / mid))}`;

            if (fits()) {
                best = mid;
                low = mid + 0.25;
            } else {
                high = mid - 0.25;
            }
        }

        el.style.fontSize = `${best}px`;
        el.style.lineHeight = `${Math.max(1.05, Math.min(1.12, safeLineHeight / best))}`;
        el.style.maxHeight = `${best * 1.12 * maxLines + 4}px`;
        el.style.overflow = "hidden";
        el.style.fontWeight = originalWeight;
    }

    function fitAll() {
        document.querySelectorAll(SELECTOR).forEach(fitHeading);
    }

    let timer = 0;
    function scheduleFit() {
        cancelAnimationFrame(timer);
        timer = requestAnimationFrame(() => {
            fitAll();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", scheduleFit, { once: true });
    } else {
        scheduleFit();
    }

    window.addEventListener("resize", scheduleFit, { passive: true });
    window.addEventListener("orientationchange", scheduleFit, { passive: true });

    const observer = new MutationObserver(scheduleFit);
    observer.observe(document.body, { childList: true, subtree: true });
})();