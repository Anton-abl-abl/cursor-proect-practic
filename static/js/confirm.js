document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement) || !form.hasAttribute("data-confirm")) {
    return;
  }
  const message = form.getAttribute("data-confirm") || "Удалить заметку?";
  if (!window.confirm(message)) {
    event.preventDefault();
  }
});
