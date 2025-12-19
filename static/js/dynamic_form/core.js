//core.js

import { renderFields } from './fields.js';
import { loadAssetTypes } from './asset-type.js';
import { handleStatusChange } from './status-remarks.js';
import { populateAvailableFeatureList } from './feature-list.js';
import { setupDatepickers } from './setup.js';
import { setMasterFields, getMasterFields, fieldConfigMap } from './globals.js';

export function fetchMasterFields() {
  return fetch("/get_master_fields")
    .then(res => res.json())
    .then(data => {
      if (Array.isArray(data.fields)) {
        setMasterFields(data.fields);
        console.log("✅ Master fields loaded:", data.fields);
      } else {
        console.error("❌ Invalid response from get_master_fields");
      }
    })
    .catch(err => console.error("❌ Failed to fetch master fields:", err));
}

export async function setupForm() {
  await fetchMasterFields();
  // Populate feature list ONLY in create mode
  if (!window.existingAssetData?.category) {
    populateAvailableFeatureList();
  }

  const createFormBtn = document.getElementById("create-form-btn");
  const form = document.getElementById("asset-form");
  const submitBtn = document.getElementById("submit-btn");
  const typeSelect = document.getElementById("asset_type");
  const newTypeWrapper = document.getElementById("new-type-wrapper");
  const featureSelectWrapper = document.getElementById("feature-select-wrapper");
  const dynamicFieldsContainer = document.getElementById("dynamic-fields");
  const statusRemarksSection = document.getElementById("status-remarks-section");

  window.form = form;

  form.addEventListener("input", () => {
    const isNewType = typeSelect.value === "add_new_type";
    if (isNewType) {
      submitBtn.disabled = !form.checkValidity() || !window.fieldsToRender || window.fieldsToRender.length === 0;
    } else {
      submitBtn.disabled = !form.checkValidity();
    }
  });

  form.addEventListener("submit", () => {
    const selectedFeatures = Array.from(document.querySelectorAll("input[name='feature_checkbox']:checked"))
      .map(cb => cb.value.trim());
    document.getElementById("selected_features").value = selectedFeatures.join(",");

    const customFieldInputs = Array.from(document.querySelectorAll(".custom-field"));
    const customFieldStr = customFieldInputs.map(input => {
      const label = input.dataset.label;
      const name = input.dataset.name;
      const type = input.dataset.type;
      return `${label}:${name}:${type}`;
    }).join("|");
    document.getElementById("custom_fields").value = customFieldStr;

    form.querySelectorAll("input[data-value]").forEach(input => {
      const raw = input.getAttribute("data-value");
      input.value = raw || "0";
    });

    form.querySelectorAll('input[type="date"]').forEach(input => {
      if (input.value.includes("-")) {
        const parts = input.value.split("-");
        input.value = `${parts[2]}-${parts[1]}-${parts[0]}`;
      }
    });

    console.log("📝 Final form values before submission:");
    const formData = new FormData(form);
    for (let [key, val] of formData.entries()) {
      console.log(`${key}: ${val}`);
    }
  });

//Attach change handler ONLY in create mode
if (!window.existingAssetData?.category) {
  typeSelect.addEventListener("change", () => {
    const selectedType = typeSelect.value;
    const isAddNew = selectedType === "add_new_type";

    newTypeWrapper.hidden = !isAddNew;
    featureSelectWrapper.hidden = !isAddNew;
    createFormBtn.hidden = !isAddNew;

    if (isAddNew) {
      document.querySelectorAll("input[name='feature_checkbox']").forEach(cb => cb.checked = false);

      localStorage.removeItem("selectedFeatures");
      sessionStorage.removeItem("selectedFeatures");

      const hiddenFeatureInput = document.getElementById("selected_features");
      if (hiddenFeatureInput) hiddenFeatureInput.value = "";

      window.fieldsToRender = [];
      dynamicFieldsContainer.innerHTML = "";
    } else {
      if (!fieldConfigMap[selectedType] || window.renderedTypeOnce !== selectedType) {
        renderFields(selectedType, {});
        window.renderedTypeOnce = selectedType;
      }
      statusRemarksSection.hidden = false;
    }

    form.dispatchEvent(new Event("input"));
  });
}


  handleStatusChange(form);
  loadAssetTypes();
  setupDatepickers();
/*
  if (window.fieldsToRender && window.fieldsToRender.length > 0 && window.existingAssetData) {
    const selectedType = window.existingAssetData.category;
    fieldConfigMap[selectedType] = window.fieldsToRender;
    renderFields(selectedType, window.existingAssetData);
    delete window.existingAssetData;
  }
  */ 
  //FIXED "Create Form" button: only renders fields, does NOT save
  createFormBtn.addEventListener("click", () => {
    createFormBtn.disabled = true;

    const selectedFeatures = Array.from(
      document.querySelectorAll("input[name='feature_checkbox']:checked")
    ).map(cb => cb.value);

    if (selectedFeatures.length === 0) {
      alert("Please select at least one field.");
      createFormBtn.disabled = false;
      return;
    }

    const realType = document.getElementById("new-type")?.value?.trim();
    if (!realType) {
      alert("Please enter a name for the new type.");
      createFormBtn.disabled = false;
      return;
    }

    const fieldsToInject = getMasterFields().filter(f =>
      selectedFeatures.includes(f.name)
    );
    window.fieldsToRender = fieldsToInject;
    fieldConfigMap[realType] = fieldsToInject;

    renderFields(realType, {});
    form.dispatchEvent(new Event("input"));
    submitBtn.disabled = false;

    createFormBtn.disabled = false; // Re-enable button
  });
}


/*export function loadAssetTypes() {
  const typeSelect = document.getElementById("asset_type");
  const statusRemarksSection = document.getElementById("status-remarks-section");

  const isEdit = Boolean(window.existingAssetData?.category);
  const selectedCategory = window.existingAssetData?.category || "";

  fetch("/get_asset_types")
    .then(res => res.json())
    .then(types => {
      // 🔥 CLEAR first
      typeSelect.innerHTML = "";

      // ✅ EDIT MODE: inject ONLY the existing category
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
*/