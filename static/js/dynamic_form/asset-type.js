//asset-type.js

import { renderFields } from './fields.js';

export function loadAssetTypes() {
  const typeSelect = document.getElementById("asset_type");
  const statusRemarksSection = document.getElementById("status-remarks-section");

  const isEdit = Boolean(window.existingAssetData?.category);
  const selectedCategory = window.existingAssetData?.category || "";

  fetch("/get_asset_types")
    .then(res => res.json())
    .then(types => {
      // CLEAR first
      typeSelect.innerHTML = "";

      // EDIT MODE: inject ONLY the existing category
      if (isEdit) {
        const opt = document.createElement("option");
        opt.value = selectedCategory;
        opt.textContent = selectedCategory;
        opt.selected = true;
        typeSelect.appendChild(opt);

        typeSelect.disabled = true;
        typeSelect.classList.add("bg-secondary-subtle");
        typeSelect.title = "Asset category cannot be changed";

        renderFields(selectedCategory, window.existingAssetData);
        statusRemarksSection.hidden = false;
        return; // ⛔ STOP HERE — VERY IMPORTANT
      }

      // 🆕 CREATE MODE ONLY
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Select asset type";
      placeholder.disabled = true;
      placeholder.selected = true;
      typeSelect.appendChild(placeholder);

      types.forEach(type => {
        const opt = document.createElement("option");
        opt.value = type;
        opt.textContent = type;
        typeSelect.appendChild(opt);
      });

      const newOpt = document.createElement("option");
      newOpt.value = "add_new_type";
      newOpt.textContent = "➕ Add New Type";
      typeSelect.appendChild(newOpt);
    })
    .catch(err => {
      console.error("Error loading asset types:", err);
    });
}

/*export function loadAssetTypes() {
  const typeSelect = document.getElementById("asset_type");
  const statusRemarksSection = document.getElementById("status-remarks-section");

  fetch("/get_asset_types")
    .then(res => res.json())
    .then(types => {
      const isEdit = !!window.existingAssetData?.category;
      const existingType = window.existingAssetData?.category;

      // 🔹 STEP 1: Initialize dropdown correctly
      if (isEdit) {
        typeSelect.innerHTML = `
          <option value="${existingType}" selected>
            ${existingType}
          </option>
        `;
      } else {
        typeSelect.innerHTML = `<option disabled selected value="">Select asset type</option>`;
      }

      // 🔹 STEP 2: Append other types (skip current in edit)
      types.forEach(type => {
        if (isEdit && type === existingType) return;

        const opt = document.createElement("option");
        opt.value = opt.textContent = type;
        typeSelect.appendChild(opt);
      });

      // 🔹 STEP 3: Add "Add New Type" ONLY in create mode
      if (!isEdit) {
        const newOpt = document.createElement("option");
        newOpt.value = "add_new_type";
        newOpt.textContent = "➕ Add New Type";
        typeSelect.appendChild(newOpt);
      }

      // 🔹 STEP 4: Render fields + lock dropdown (THIS IS THE RIGHT PLACE)
      if (isEdit) {
        typeSelect.value = existingType;
        typeSelect.disabled = true;
        typeSelect.classList.add("bg-secondary-subtle");
        typeSelect.title = "Asset category cannot be changed";

        renderFields(existingType);
        statusRemarksSection.hidden = false;
      }
    })
    .catch(err => {
      console.error("Error loading asset types:", err);
    });
}

*/