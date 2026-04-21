(function () {
    function injectFavicon() {
        const ts = Math.floor(Date.now() / 3600000); // update per jam

        // Remove existing favicon links
        document
            .querySelectorAll("link[rel~='icon'], link[rel='apple-touch-icon'], link[rel='manifest']")
            .forEach((el) => el.remove());

        // Favicon ICO
        const faviconLink = document.createElement("link");
        faviconLink.rel = "icon";
        faviconLink.type = "image/x-icon";
        faviconLink.href = `/ld_favicon/favicon.ico?v=${ts}`;
        document.head.appendChild(faviconLink);

        // Apple touch icon
        const appleLink = document.createElement("link");
        appleLink.rel = "apple-touch-icon";
        appleLink.href = `/ld_favicon/apple-touch-icon.png?v=${ts}`;
        document.head.appendChild(appleLink);

        // Web manifest
        const manifestLink = document.createElement("link");
        manifestLink.rel = "manifest";
        manifestLink.href = `/ld_favicon/site.webmanifest?v=${ts}`;
        document.head.appendChild(manifestLink);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", injectFavicon);
    } else {
        injectFavicon();
    }
})();
