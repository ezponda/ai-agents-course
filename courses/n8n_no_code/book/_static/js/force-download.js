/**
 * Enhanced download functionality for Jupyter Book
 * - Force download for .md / .ipynb source files (GitHub Pages serves them as text/plain)
 * - Add HTML download option
 */
(function() {
    // Prevent running twice
    if (window._forceDownloadInitialized) return;
    window._forceDownloadInitialized = true;

    document.addEventListener('DOMContentLoaded', function() {
        // Add HTML download option to dropdown
        addDownloadOptions();

        // Force download for .md / .ipynb source files
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href$=".md"], a[href$=".ipynb"]');
            if (!link) return;

            const isDownloadLink = link.closest('.dropdown-menu') ||
                                   link.classList.contains('download') ||
                                   link.closest('.sd-card-body');

            if (!isDownloadLink) return;

            e.preventDefault();
            e.stopPropagation();
            forceDownload(link.href, link.href.split('/').pop());
        }, true);
    });
})();

/**
 * Add HTML download option to the dropdown
 * (.md is no longer added here: the source files are Markdown, so the
 * theme's own source-download entry already provides it)
 */
function addDownloadOptions() {
    const dropdown = document.querySelector('.dropdown-download-buttons .dropdown-menu');
    if (!dropdown) return;

    // Prevent duplicate additions
    if (dropdown.querySelector('.download-html-btn')) return;

    const baseFilename = window.location.pathname.split('/').pop().replace('.html', '') || 'page';

    // HTML download option
    const htmlLi = document.createElement('li');
    htmlLi.innerHTML = `
        <a href="#" class="btn btn-sm dropdown-item download-html-btn"
           title="Download as HTML" data-bs-placement="left" data-bs-toggle="tooltip">
            <span class="btn__icon-container"><i class="fas fa-code"></i></span>
            <span class="btn__text-container">.html</span>
        </a>`;
    dropdown.appendChild(htmlLi);

    // HTML download handler
    htmlLi.querySelector('a').addEventListener('click', function(e) {
        e.preventDefault();
        const html = document.documentElement.outerHTML;
        const blob = new Blob([html], { type: 'text/html' });
        downloadBlob(blob, baseFilename + '.html');
    });
}

/**
 * Force download a URL as a file
 */
function forceDownload(url, filename) {
    fetch(url)
        .then(response => response.blob())
        .then(blob => downloadBlob(blob, filename))
        .catch(err => {
            console.error('Download failed:', err);
            window.open(url, '_blank');
        });
}

/**
 * Download a blob as a file
 */
function downloadBlob(blob, filename) {
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(blobUrl);
}
