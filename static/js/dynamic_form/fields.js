//fields.js

import { attachCurrencyFormat, calculateTotal } from './currency.js';
import { fieldConfigMap } from './globals.js';
import { isFutureDate } from './utils.js'; 

export function renderFields(assetType, data = {}) {
  const form = window.form;
  const dynamicFieldsContainer = document.getElementById("dynamic-fields");

  console.log("🔀 Rendering fields for:", assetType);

  dynamicFieldsContainer.innerHTML = "";

  const assetTypeInput = form.querySelector('[name="category"]');
  if (assetTypeInput) {
    assetTypeInput.value = assetType;
  }

  let config = fieldConfigMap[assetType];
  if (!config) {
    fetch(`/get_fields/${encodeURIComponent(assetType)}`)
      .then(res => res.json())
      .then(response => {
          console.log(` Response for ${assetType}:`, response);

          const config = response.fields;

          if (!Array.isArray(config) || config.length === 0) {
            console.warn("🚫 No fields to render for:", assetType);
            dynamicFieldsContainer.innerHTML =
              `<div class="text-danger mb-3">No field config available for "${assetType}".</div>`;
            return;
          }

          fieldConfigMap[assetType] = config;

          // IMPORTANT: pass ASSET DATA, not API response
          injectFields(config, data);
        })
      .catch(err => {
        console.error("Failed to fetch dynamic fields:", err);
        dynamicFieldsContainer.innerHTML = `<div class="text-danger">Failed to load form configuration.</div>`;
      });
  } else {
    console.log("📦 Fetched config:", config);
    console.log("✅ Passing data to injectFields:", data);
    injectFields(config, data);
  }
}

export function injectFields(config, data = {}) {
  console.log("📥 Received data in injectFields:", data);

  const form = window.form;
  const dynamicFieldsContainer = document.getElementById("dynamic-fields");

  dynamicFieldsContainer.innerHTML = "";

  config.forEach((field, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "mb-3";

    const label = document.createElement("label");
    label.className = "form-label";
    label.textContent = field.label;

    let input;
    const isCurrency = ["amount", "total"].includes(field.name) || field.name.startsWith("gst_");

    const existingValue = data[field.name];
    console.log(`🔎 Matching field: ${field.name} -> value:`, existingValue);

    if (field.type === "select") {
      // Handle select dropdowns
      if (!field.options || field.options.length === 0) {
        if (field.name === "status") {
          field.options = ["Available(p)", "Available(g)", "Assigned(p)", "Assigned(g)", "Repair/Faulty", "Discard"];
        } else if (field.name === "state") {
          field.options = [ /* states */ "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
            "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
            "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"];
        }
      }

      input = document.createElement("select");
      input.className = "form-select";
      input.name = field.name;

      const defaultOption = document.createElement("option");
      defaultOption.disabled = true;
      defaultOption.value = "";
      defaultOption.textContent = `Select ${field.label}`;
      input.appendChild(defaultOption);

      field.options.forEach(option => {
        const opt = document.createElement("option");
        opt.value = option;
        opt.textContent = option;

        if (
          existingValue &&
          existingValue.toString().toLowerCase() === option.toLowerCase()
        ) {
          opt.selected = true;
          defaultOption.selected = false;
        }

        input.appendChild(opt);
      });

      if (!existingValue) defaultOption.selected = true;

      wrapper.appendChild(label);
      wrapper.appendChild(input);

    } else if (isCurrency) {
      // Handle currency fields (amount, gst, total)
      const group = document.createElement("div");
      group.className = "input-group";

      const prefix = document.createElement("span");
      prefix.className = "input-group-text";
      prefix.textContent = "₹";

      input = document.createElement("input");
      input.className = "form-control";
      input.name = field.name;
      input.type = "text";

      attachCurrencyFormat(input); // 🟢 Attach plugin first

      if (existingValue !== undefined && existingValue !== null && existingValue !== "") {
        const raw = existingValue.toString().replace(/[^0-9.]/g, "");
        const numeric = parseFloat(raw);

        if (!isNaN(numeric)) {
          input.setAttribute("data-value", numeric.toFixed(2));

          if (field.name === "amount") {
            input.value = "";
            setTimeout(() => {
              input.value = numeric.toFixed(2);
              input.dispatchEvent(new Event("input"));
            }, 0);
          } else {
            input.value = numeric.toLocaleString("en-IN", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            });
          }
        }
        }  

      if (field.name === "total") input.readOnly = true;

      group.appendChild(prefix);
      group.appendChild(input);
      wrapper.appendChild(label);
      wrapper.appendChild(group);

    } else {
      // Handle regular text or date inputs
      input = document.createElement("input");
      input.className = "form-control";
      input.name = field.name;
      input.type = field.type === "date" ? "text" : (field.type || "text");

      if (existingValue !== undefined && existingValue !== null) {
        input.value = existingValue;
      }

      if (field.type === "date") {
        input.placeholder = "DD-MM-YYYY";
        input.dataset.format = "d-m-Y";
      }

      wrapper.appendChild(label);
      wrapper.appendChild(input);
    }

    input.setAttribute("tabindex", index + 1);
    console.log("⬅️ Injecting field:", {
      label: field.label,
      name: input.name,
      value: input.value,
      type: input.type,
      hasNameAttr: input.hasAttribute("name"),
    });

    dynamicFieldsContainer.appendChild(wrapper);
  });

  calculateTotal();

  const hasStatus = config.some(f => f.name === "status");
  const hasRemarks = config.some(f => f.name === "remarks");

  const statusRemarksSection = document.getElementById("status-remarks-section");
  if (statusRemarksSection) {
    statusRemarksSection.hidden = hasStatus || hasRemarks;
  }

  flatpickr("input[data-format='d-m-Y']", {
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

  form.dispatchEvent(new Event("input"));
}

window.injectFields = injectFields;
window.renderFields = renderFields;
window.fieldConfigMap = fieldConfigMap;
