import commonjs from '@rollup/plugin-commonjs';
import { nodeResolve } from '@rollup/plugin-node-resolve';

export default {
  input: 'C:/Users/Admin/Downloads/AMS/static/js/dynamic_form/index.js',
  output: {
    file: 'public/assets/bundle.js',
    format: 'iife'
  },
  plugins: [
    nodeResolve(),
    commonjs()
  ]
};
