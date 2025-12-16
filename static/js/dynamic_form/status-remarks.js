// 📁 dynamic_form/status-remarks.js

/**
 * Highlights the "remarks" field based on selected status.
 * Triggered on status field change.
 */
export function handleStatusChange(event) {
  const status = event.target.value?.toLowerCase();
  const remarksField = document.querySelector('[name="remarks"]');
  if (!remarksField) return;

  const highlight = ["discard", "repair/faulty"].includes(status);

  Object.assign(remarksField.style, {
    color: highlight ? "red" : "",
    fontWeight: highlight ? "bold" : "",
    textTransform: highlight ? "uppercase" : ""
  });
}
