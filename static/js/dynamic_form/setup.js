//setup.js
import flatpickr from "flatpickr";
import { isFutureDate } from "./utils.js";

/**
 * Initializes flatpickr datepickers and restricts native date inputs.
 * - Applies DD-MM-YYYY format
 * - Disallows future dates
 */
export function setupDatepickers() {
  setTimeout(() => {
    document.querySelectorAll('input[placeholder="DD-MM-YYYY"]').forEach(input => {
      flatpickr(input, {
        dateFormat: "d-m-Y",
        maxDate: "today",
        allowInput: true,
        onClose(selectedDates, dateStr, instance) {
          const selected = selectedDates[0];
          if (selected && isFutureDate(selected)) {
            alert("Future dates are not allowed.");
            instance.clear();
          }
        }
      });
    });
  }, 500);

  const today = new Date().toISOString().split("T")[0];

  document.querySelectorAll('input[type="date"]').forEach(input => {
    input.setAttribute("max", today);

    const parsed = flatpickr.parseDate(input.value, "d-m-Y");
    if (parsed && isFutureDate(parsed)) {
      alert("Future dates are not allowed.");
      input.value = "";
    }
  });
}
