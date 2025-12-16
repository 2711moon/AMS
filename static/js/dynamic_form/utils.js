//utils.js
// Pure utility functions (minimal DOM interaction)

/**
 * Checks if a given date is in the future.
 * @param {Date} date
 * @returns {boolean}
 */
export function isFutureDate(date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Normalize to midnight
  return date > today;
}

/**
 * Briefly highlights an input element for visual feedback.
 * @param {HTMLElement} input
 */
export function flashInput(input) {
  input.classList.add("bg-warning-subtle");
  setTimeout(() => input.classList.remove("bg-warning-subtle"), 800);
}
