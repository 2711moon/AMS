import path from "path";
import commonjs from "@rollup/plugin-commonjs";
import { nodeResolve } from "@rollup/plugin-node-resolve";

export default {
  input: path.resolve("static/js/dynamic_form/index.js"),
  output: {
    file: path.resolve("public/assets/bundle.js"),
    format: "iife",
    sourcemap: true
  },
  plugins: [
    nodeResolve(),
    commonjs()
  ]
};
