// Light/dark toggle. The choice is remembered per browser; without one, the site follows the system setting.
(function () {
  var root = document.documentElement;
  var media = matchMedia("(prefers-color-scheme: dark)");
  var btn = null;

  function saved() { try { return localStorage.getItem("theme"); } catch (e) { return null; } }
  function isDark() { return root.dataset.theme ? root.dataset.theme === "dark" : media.matches; }
  function label() {
    if (!btn) return;
    var text = isDark() ? "Switch to light mode" : "Switch to dark mode";
    btn.setAttribute("aria-label", text);
    btn.title = text;
  }
  // Re-read the saved choice: needed when a page comes back from the back/forward cache
  // or when the choice changed in another tab.
  function sync() {
    var t = saved();
    if (t) root.dataset.theme = t; else delete root.dataset.theme;
    label();
  }

  window.addEventListener("pageshow", function (e) { if (e.persisted) sync(); });
  window.addEventListener("storage", function (e) { if (e.key === "theme") sync(); });
  if (media.addEventListener) media.addEventListener("change", label);

  document.addEventListener("DOMContentLoaded", function () {
    btn = document.querySelector(".theme-toggle");
    if (!btn) return;
    sync();
    btn.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) {}
      label();
    });
  });
})();
