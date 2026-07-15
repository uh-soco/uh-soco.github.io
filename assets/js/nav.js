(function () {
  // Dropdowns are <ds-action-menu> — the component manages its own
  // open/close/focus behaviour. We only need to wire navigation, since
  // <ds-action-list-item> has no href of its own.
  document.querySelectorAll("ds-action-list-item[data-url]").forEach(function (item) {
    item.addEventListener("dsSelect", function () {
      window.location.href = item.dataset.url;
    });
  });

  // Mobile nav list toggle.
  var mobileToggle = document.querySelector(".site-nav__mobile-toggle");
  var navList = document.getElementById("site-nav-list");
  if (mobileToggle && navList) {
    mobileToggle.addEventListener("click", function () {
      var isOpen = navList.classList.toggle("is-open");
      mobileToggle.setAttribute("ds-aria-expanded", String(isOpen));
    });
  }
})();
