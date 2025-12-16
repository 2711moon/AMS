// 📁 dynamic_form/asset-type.js

import { renderFields } from './fields.js';

export function loadAssetTypes() {
  const typeSelect = document.getElementById("asset_type");
  const statusRemarksSection = document.getElementById("status-remarks-section");

  fetch("/get_asset_types")
    .then(res => res.json())
    .then(types => {
      typeSelect.innerHTML = `<option disabled selected value="">Select asset type</option>`;

      types.forEach(type => {
        const opt = document.createElement("option");
        opt.value = opt.textContent = type;
        typeSelect.appendChild(opt);
      });

      const newOpt = document.createElement("option");
      newOpt.value = "add_new_type";
      newOpt.textContent = "➕ Add New Type";
      typeSelect.appendChild(newOpt);

      const existingType = window.existingAssetData?.category;
      if (existingType && existingType !== "add_new_type") {
        const optionExists = [...typeSelect.options].some(opt => opt.value === existingType);
        if (!optionExists) {
          const opt = document.createElement("option");
          opt.value = opt.textContent = existingType;
          typeSelect.prepend(opt);
        }

        typeSelect.value = existingType;
        renderFields(existingType);
        statusRemarksSection.hidden = false;
      }
    })
    .catch(err => {
      console.error("Error loading asset types:", err);
    });
}
