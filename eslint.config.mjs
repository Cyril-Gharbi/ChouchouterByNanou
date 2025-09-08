// eslint.config.mjs
import js from "@eslint/js";

export default [
  // 1️⃣ Fichiers et dossiers à ignorer
  {
    ignores: [
      "venv/**",               // ignorer l'environnement virtuel Python
      "app/static/vendor/**",  // ignorer les librairies tierces
      "app/static/*.min.js",   // ignorer les fichiers minifiés
    ],
  },

  // 2️⃣ Configuration de base recommandée
  js.configs.recommended,

  // 3️⃣ Règles personnalisées pour ton projet
  {
    languageOptions: {
      globals: {
        window: "readonly",
        document: "readonly",
        console: "readonly",
        alert: "readonly",
        fetch: "readonly",
      },
    },
    rules: {
      "no-unused-vars": "warn",   // avertissement pour variables inutilisées
      "no-console": "off",        // autorise console.log
      "no-undef": "error",        // erreur si variable non déclarée
      "semi": ["error", "always"], // points-virgules obligatoires
      "indent": ["warn", 2],      // indentation 2 espaces
      "object-curly-spacing": ["warn", "always"], // espaces dans accolades
      "quotes": ["error", "single"],               // quotes simples
      "no-redeclare": "error",     // pas de redéclaration de variables
      "eqeqeq": ["warn", "always"], // préférer === à ==
      "no-empty": ["warn"],        // avertissement pour blocs vides
    },
  },
];
