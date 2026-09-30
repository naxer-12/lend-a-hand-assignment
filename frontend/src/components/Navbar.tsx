"use client";

import React from "react";
import { Globe, Eye, ShieldCheck, Landmark } from "lucide-react";
import { translations } from "@/lib/i18n";
import { Language } from "@/types";

interface NavbarProps {
  lang: Language;
  onLanguageToggle: () => void;
  highContrast: boolean;
  onContrastToggle: () => void;
}

export default function Navbar({
  lang,
  onLanguageToggle,
  highContrast,
  onContrastToggle,
}: NavbarProps) {
  const t = translations[lang];

  return (
    <header
      role="banner"
      className={`border-b transition-colors duration-200 ${
        highContrast
          ? "bg-black text-yellow-400 border-yellow-400"
          : "bg-white text-gray-900 border-gray-200"
      }`}
    >
      {/* Skip to Main Content Link for WCAG Screen Readers */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-indigo-600 focus:text-white focus:rounded focus:outline-none focus:ring-4 focus:ring-yellow-400"
      >
        Skip to main content / મુખ્ય સામગ્રી પર જાઓ
      </a>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Brand & State Government Identity */}
          <div className="flex items-center space-x-3">
            <div
              className={`p-2 rounded-lg flex items-center justify-center ${
                highContrast
                  ? "bg-yellow-400 text-black font-bold"
                  : "bg-gradient-to-br from-indigo-700 to-blue-600 text-white shadow-sm"
              }`}
              aria-hidden="true"
            >
              <Landmark className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight leading-tight">
                  {t.portalTitle}
                </h1>
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${
                    highContrast
                      ? "bg-yellow-400 text-black border border-black"
                      : "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  }`}
                  role="status"
                  aria-live="polite"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
                  {t.liveStatus}
                </span>
              </div>
              <p
                className={`text-xs ${
                  highContrast ? "text-yellow-200" : "text-gray-500"
                }`}
              >
                {t.governmentSubtitle}
              </p>
            </div>
          </div>

          {/* Accessibility & Localization Toolbars (Q9: WCAG 2.1 AA) */}
          <div className="flex items-center flex-wrap gap-2.5">
            {/* High Contrast Mode Toggle */}
            <button
              type="button"
              onClick={onContrastToggle}
              aria-label={`Toggle high contrast mode. Currently ${
                highContrast ? "enabled" : "disabled"
              }`}
              aria-pressed={highContrast}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
                highContrast
                  ? "bg-yellow-400 text-black hover:bg-yellow-300 focus-visible:ring-yellow-400 font-bold"
                  : "bg-gray-100 text-gray-800 hover:bg-gray-200 border border-gray-300 focus-visible:ring-indigo-600"
              }`}
            >
              <Eye className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{highContrast ? t.normalContrast : t.highContrast}</span>
            </button>

            {/* Language Switcher (EN <-> GU) */}
            <button
              type="button"
              onClick={onLanguageToggle}
              aria-label={`Switch language to ${lang === "en" ? "Gujarati" : "English"}`}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
                highContrast
                  ? "border border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black focus-visible:ring-yellow-400"
                  : "bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 focus-visible:ring-indigo-600"
              }`}
            >
              <Globe className="w-3.5 h-3.5" aria-hidden="true" />
              <span className="font-semibold">{t.switchLanguage}</span>
            </button>

            {/* WCAG 2.1 AA Compliance Badge */}
            <div
              className={`hidden lg:flex items-center gap-1 px-2.5 py-1 text-xs rounded border ${
                highContrast
                  ? "border-yellow-400 text-yellow-400"
                  : "border-gray-200 text-gray-500 bg-gray-50"
              }`}
              title="Complies with Web Content Accessibility Guidelines 2.1 Level AA"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" aria-hidden="true" />
              <span>{t.wcagBadge}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
