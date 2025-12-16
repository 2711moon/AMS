// 📁 dynamic_form/feature-list.js

import { getMasterFields } from "./globals.js";

/**
 * Populates the UI with a list of available fields as checkboxes,
 * and enables building a dynamic form from selected fields.
 */
export function populateAvailableFeatureList() {
  const listDiv = document.getElementById("available-feature-list");
  listDiv.innerHTML = "";

  const masterFields = getMasterFields();

  masterFields.forEach((field, index) => {
    const wrapper = document.createElement("div");

    const checkbox = Object.assign(document.createElement("input"), {
      type: "checkbox",
      id: `feature_${index}`,
      name: "feature_checkbox",
      value: field.name,
    });

    const label = Object.assign(document.createElement("label"), {
      htmlFor: checkbox.id,
      textContent: field.label,
      style: "margin-left: 6px"
    });

    wrapper.append(checkbox, label);
    listDiv.appendChild(wrapper);
  });
}
