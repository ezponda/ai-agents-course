// Add translate button next to the article header buttons
document.addEventListener('DOMContentLoaded', function() {
  // Find the article header buttons container
  const headerButtons = document.querySelector('.article-header-buttons');
  if (headerButtons) {
    // Check if button already exists (avoid duplicates)
    if (headerButtons.querySelector('.translate-btn')) return;

    // Create the translate button
    const translateBtn = document.createElement('button');
    translateBtn.className = 'btn btn-sm nav-link translate-btn';
    translateBtn.title = 'Traducir página (Google Translate)';
    translateBtn.setAttribute('aria-label', 'Translate to Spanish');
    translateBtn.innerHTML = '<i class="fas fa-globe"></i>';
    translateBtn.style.cssText = 'border: none; background: transparent; cursor: pointer;';

    translateBtn.onclick = function() {
      // Open Google Translate in a new tab with the page URL
      const url = encodeURIComponent(window.location.href);
      window.open('https://translate.google.com/translate?sl=en&tl=es&hl=es&u=' + url, '_blank');
    };

    // Insert at the beginning of the header buttons
    headerButtons.insertBefore(translateBtn, headerButtons.firstChild);
  }
});
