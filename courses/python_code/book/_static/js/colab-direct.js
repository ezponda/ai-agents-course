// Turn the "launch" dropdown (which has only one item, Colab) into a direct link:
// clicking the toolbar button opens the current notebook in Colab, no dropdown.
window.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".dropdown-launch-buttons").forEach(function (dd) {
    var link = dd.querySelector(".dropdown-menu a[href]");
    var btn = dd.querySelector(".dropdown-toggle");
    if (!link || !btn) return;
    var url = link.href;
    btn.removeAttribute("data-bs-toggle"); // stop Bootstrap from opening the dropdown
    btn.setAttribute("title", "Open in Colab");
    btn.setAttribute("aria-label", "Open in Colab");
    btn.addEventListener(
      "click",
      function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        window.open(url, "_blank", "noopener");
      },
      true
    );
  });
});
