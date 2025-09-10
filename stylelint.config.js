module.exports = {
  extends: [
    "stylelint-config-standard"
  ],
  plugins: [
    "stylelint-order"
  ],
  rules: {
    "color-no-invalid-hex": true,
    "block-no-empty": true,
    "order/properties-alphabetical-order": true
  }
};
