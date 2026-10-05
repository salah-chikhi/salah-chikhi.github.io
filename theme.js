// Light/dark toggle. The choice is remembered per browser; without one, the site follows the system setting.
(function () {
  var root = document.documentElement;
  var media = matchMedia("(prefers-color-scheme: dark)");
  function isDark() { return root.dataset.theme ? root.dataset.theme === "dark" : media.matches; }
  function label(btn) {
    var text = isDark() ? "Switch to light mode" : "Switch to dark mode";
    btn.setAttribute("aria-label", text);
    btn.title = text;
  }
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.querySelector(".theme-toggle");
    if (!btn) return;
    label(btn);
    btn.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) {}
      label(btn);
    });
    if (media.addEventListener) media.addEventListener("change", function () { label(btn); });
  });
})();
