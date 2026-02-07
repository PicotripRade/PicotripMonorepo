import i18n from "i18next";
import { initReactI18next } from "react-i18next";

// Importuj JSON fajlove direktno
import translationEN from "../locales/en.json";
import translationSR from "../locales/sr.json";
import translationFR from "../locales/fr.json";

console.log("I18N FAJL SE POKREĆE!");

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: translationEN },
      sr: { translation: translationSR },
      fr: { translation: translationFR }
    },
    lng: "en",
    fallbackLng: "en",
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;