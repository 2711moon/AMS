//index.js

// Entry point: initializes the asset form logic and datepickers

import { setupForm } from "./core.js";
import { setupDatepickers } from "./setup.js";

// Run setup once DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  setupForm();
  setupDatepickers();
});
