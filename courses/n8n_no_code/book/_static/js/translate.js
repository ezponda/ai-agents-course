// Add translate button - with global flag to prevent ANY duplicates
(function() {
  // Global flag to ensure this only runs once, even if script is loaded multiple times
  if (window._translateButtonAdded) return;
  window._translateButtonAdded = true;

  document.addEventListener('DOMContentLoaded', function() {
    const headerButtons = document.querySelector('.article-header-buttons');
    if (!headerButtons) return;

    // Create the translate button
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm nav-link';
    btn.title = 'Traducir página (Google Translate)';
    btn.innerHTML = '<i class="fas fa-globe"></i>';
    btn.style.cssText = 'border:none;background:transparent;cursor:pointer;';
    btn.onclick = function() {
      window.open('https://translate.google.com/translate?sl=en&tl=es&hl=es&u=' + encodeURIComponent(window.location.href), '_blank');
    };

    headerButtons.insertBefore(btn, headerButtons.firstChild);
  });
})();
