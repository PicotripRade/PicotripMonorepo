// src/components/languageSwitcher/LanguageSwitcher.jsx
import React from "react";
import { useTranslation } from "react-i18next";
import "./languageSwitcher.css";

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="language-switcher">
      <button
        className={i18n.language === "en" ? "active" : ""}
        onClick={() => changeLanguage("en")}
      >
        EN
      </button>
      <button
        className={i18n.language === "sr" ? "active" : ""}
        onClick={() => changeLanguage("sr")}
      >
        SR
      </button>
    </div>
  );
};

export default LanguageSwitcher;

