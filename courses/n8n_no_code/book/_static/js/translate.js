// Add translate button next to the article header buttons
document.addEventListener('DOMContentLoaded', function() {
  // Find the article header buttons container
  const headerButtons = document.querySelector('.article-header-buttons');
  if (headerButtons) {
    // Create the translate button
    const translateBtn = document.createElement('button');
    translateBtn.className = 'btn btn-sm nav-link';
    translateBtn.title = 'Translate to Spanish';
    translateBtn.setAttribute('aria-label', 'Translate to Spanish');
    translateBtn.innerHTML = '<i class="fas fa-globe"></i>';
    translateBtn.style.cssText = 'border: none; background: transparent; cursor: pointer;';

    translateBtn.onclick = function() {
      if (window.location.protocol === 'file:') {
        alert('Translation only works on the online version');
      } else {
        window.location.href = 'https://translate.google.com/translate?sl=en&tl=es&u=' + encodeURIComponent(window.location.href);
      }
    };

    // Insert at the beginning of the header buttons
    headerButtons.insertBefore(translateBtn, headerButtons.firstChild);
  }
});
