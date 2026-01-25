/**
 * Enhanced download functionality for Jupyter Book
 * - Force download for .ipynb files (GitHub Pages serves as text/plain)
 * - Add HTML and Markdown download options
 */
(function() {
    // Prevent running twice
    if (window._forceDownloadInitialized) return;
    window._forceDownloadInitialized = true;

    document.addEventListener('DOMContentLoaded', function() {
        // Add HTML and Markdown download options to dropdown
        addDownloadOptions();

        // Force download for .ipynb files
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href$=".ipynb"]');
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
 * Add HTML and Markdown download options to the dropdown
 */
function addDownloadOptions() {
    const dropdown = document.querySelector('.dropdown-download-buttons .dropdown-menu');
    if (!dropdown) return;

    // Prevent duplicate additions
    if (dropdown.querySelector('.download-html-btn')) return;

    const pageName = document.querySelector('h1')?.textContent?.trim() || 'page';
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

    // Markdown download option
    const mdLi = document.createElement('li');
    mdLi.innerHTML = `
        <a href="#" class="btn btn-sm dropdown-item download-md-btn"
           title="Download as Markdown" data-bs-placement="left" data-bs-toggle="tooltip">
            <span class="btn__icon-container"><i class="fab fa-markdown"></i></span>
            <span class="btn__text-container">.md</span>
        </a>`;
    dropdown.appendChild(mdLi);

    // HTML download handler
    htmlLi.querySelector('a').addEventListener('click', function(e) {
        e.preventDefault();
        const html = document.documentElement.outerHTML;
        const blob = new Blob([html], { type: 'text/html' });
        downloadBlob(blob, baseFilename + '.html');
    });

    // Markdown download handler
    mdLi.querySelector('a').addEventListener('click', function(e) {
        e.preventDefault();
        const markdown = htmlToMarkdown();
        const blob = new Blob([markdown], { type: 'text/markdown' });
        downloadBlob(blob, baseFilename + '.md');
    });
}

/**
 * Convert page content to Markdown
 */
function htmlToMarkdown() {
    const article = document.querySelector('article.bd-article') || document.querySelector('main');
    if (!article) return '# ' + document.title;

    const clone = article.cloneNode(true);

    // Remove unwanted elements
    clone.querySelectorAll('script, style, .headerlink, .dropdown-toggle, button').forEach(el => el.remove());

    let md = '# ' + (document.querySelector('h1')?.textContent?.trim() || document.title) + '\n\n';

    // Process content
    clone.querySelectorAll('h1, h2, h3, h4, h5, h6, p, pre, code, ul, ol, li, blockquote, a, strong, em, img').forEach(el => {
        const tag = el.tagName.toLowerCase();
        const text = el.textContent.trim();

        if (!text && tag !== 'img') return;

        switch(tag) {
            case 'h1': break; // Already added
            case 'h2': md += '\n## ' + text + '\n\n'; break;
            case 'h3': md += '\n### ' + text + '\n\n'; break;
            case 'h4': md += '\n#### ' + text + '\n\n'; break;
            case 'h5': md += '\n##### ' + text + '\n\n'; break;
            case 'h6': md += '\n###### ' + text + '\n\n'; break;
            case 'p':
                if (!el.closest('li')) md += text + '\n\n';
                break;
            case 'pre':
                const code = el.querySelector('code');
                const lang = code?.className?.match(/language-(\w+)/)?.[1] || '';
                md += '```' + lang + '\n' + text + '\n```\n\n';
                break;
            case 'blockquote':
                md += '> ' + text.replace(/\n/g, '\n> ') + '\n\n';
                break;
            case 'img':
                const src = el.getAttribute('src');
                const alt = el.getAttribute('alt') || '';
                if (src) md += '![' + alt + '](' + src + ')\n\n';
                break;
        }
    });

    return md.trim();
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
