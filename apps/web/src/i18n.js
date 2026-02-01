import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "./locales/en.json";
import sr from "./locales/sr.json";

i18n
  .use(LanguageDetector) // automatski detektuje jezik korisnika
  .use(initReactI18next) // povezuje sa React-om
  .init({
    resources: {
      en: { translation: en },
      sr: { translation: sr },
    },
    fallbackLng: "en",       // default jezik ako detekcija ne uspe
    interpolation: {
      escapeValue: false,    // React već escapuje vrednosti
    },
  });

export default i18n;
