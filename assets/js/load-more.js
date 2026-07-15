(function () {
  var button = document.getElementById("load-more-publications");
  var list = document.getElementById("publication-list");
  if (!button || !list) return;

  var pageSize = parseInt(button.dataset.pageSize, 10) || 25;

  button.addEventListener("click", function () {
    var hidden = list.querySelectorAll("li.is-hidden");
    for (var i = 0; i < hidden.length && i < pageSize; i++) {
      hidden[i].classList.remove("is-hidden");
      hidden[i].removeAttribute("hidden");
    }
    if (hidden.length <= pageSize) {
      button.remove();
    }
  });
})();
