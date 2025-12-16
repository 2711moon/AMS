//globals.js

export const fieldConfigMap = {};

let masterFields = [];

export function setMasterFields(fields) {
  masterFields = fields;
}

export function getMasterFields() {
  return masterFields;
}
