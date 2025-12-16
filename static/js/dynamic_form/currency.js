//currency.js
import { flashInput } from './utils.js';

export function attachCurrencyFormat(input, defaultValue = "") {
  input.setAttribute("data-value", defaultValue);
  input.placeholder = "0.00";
  input.value = defaultValue;

  input.addEventListener("input", () => {
    const raw = input.value.replace(/[^0-9.]/g, "");
    input.setAttribute("data-value", raw);

    if (input.name === "amount") {
      calculateTotal();
    }

    // 👇 Keep raw input visible while typing (no ₹ here)
    input.value = raw;
  });

  input.addEventListener("blur", () => {
    const raw = input.getAttribute("data-value");
    if (!raw || isNaN(raw)) {
      input.value = "";
      input.setAttribute("data-value", "");
      return;
    }

    const formatted = formatCurrency(raw);
    input.value = formatted;
  });

  input.addEventListener("paste", (e) => e.preventDefault());

  input.addEventListener("keypress", (e) => {
    if (!/[0-9.]$/.test(e.key)) e.preventDefault();
  });
}

function formatCurrency(val) {
  const num = parseFloat(val);
  if (isNaN(num)) return "";
  return num.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

export function calculateTotal() {
  const amountInput = form.querySelector('[name="amount"]');
  const totalInput = form.querySelector('[name="total"]');
  const gstField = [...form.elements].find(el => el.name?.startsWith("gst_"));

  if (!amountInput || !gstField || !totalInput) return;

  const gstPercent = parseFloat(gstField.name.split("_")[1]) || 0;
  const amountRaw = amountInput.getAttribute("data-value") || "0";
  const amount = parseFloat(amountRaw) || 0;

  if (!amount) {
    gstField.value = formatCurrency(0);
    gstField.setAttribute("data-value", "0.00");

    totalInput.value = formatCurrency(0);
    totalInput.setAttribute("data-value", "0.00");
    return;
  }

  const gstValue = parseFloat(((amount * gstPercent) / 100).toFixed(2));
  const totalValue = amount + gstValue;

  gstField.value = formatCurrency(gstValue);
  gstField.setAttribute("data-value", gstValue.toFixed(2));
  flashInput(gstField);

  totalInput.value = formatCurrency(totalValue);
  totalInput.setAttribute("data-value", totalValue.toFixed(2));
  flashInput(totalInput);
}
