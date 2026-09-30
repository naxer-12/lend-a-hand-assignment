"use client";

import React, { useState } from "react";
import useSWR from "swr";
import {
  LayoutDashboard,
  Trophy,
  Cpu,
  CreditCard,
  Lock,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import VirtualSchoolTable from "@/components/VirtualSchoolTable";
import TopSchoolsCard from "@/components/TopSchoolsCard";
import EligibilityChecker from "@/components/EligibilityChecker";
import DisbursementForm from "@/components/DisbursementForm";
import AuditVerification from "@/components/AuditVerification";
import { translations } from "@/lib/i18n";
import { Language, School, TopSchool } from "@/types";
import { fetchSchools, fetchTopSchools } from "@/lib/api";

export default function DashboardPage() {
  const [lang, setLang] = useState<Language>("en");
  const [highContrast, setHighContrast] = useState(false);
  const [activeTab, setActiveTab] = useState<"dashboard" | "top" | "rules" | "dbt" | "audit">("dashboard");

  const t = translations[lang];

  // SWR Data Fetching for High-Scale 1,000+ Schools Registry
  const { data: schoolsData, isLoading: schoolsLoading } = useSWR<School[]>(
    "api/schools/all",
    () => fetchSchools(undefined, undefined, 1200),
    { revalidateOnFocus: false, dedupingInterval: 60000 }
  );

  // SWR Data Fetching for Top 5 Schools (Q4 raw SQL query)
  const { data: topSchoolsData, isLoading: topSchoolsLoading } = useSWR<TopSchool[]>(
    "api/schools/top-enrollment",
    fetchTopSchools,
    { revalidateOnFocus: false }
  );

  const toggleLanguage = () => {
    setLang((prev) => (prev === "en" ? "gu" : "en"));
  };

  const toggleHighContrast = () => {
    setHighContrast((prev) => !prev);
  };

  const schools = schoolsData || [];
  const topSchools = topSchoolsData || [];

  return (
    <div
      className={`min-h-screen transition-colors duration-200 ${
        highContrast ? "bg-black text-yellow-400" : "bg-slate-50 text-gray-900"
      }`}
    >
      {/* Accessible Navbar with Language & Contrast Toggles */}
      <Navbar
        lang={lang}
        onLanguageToggle={toggleLanguage}
        highContrast={highContrast}
        onContrastToggle={toggleHighContrast}
      />

      {/* Main Content Area */}
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Navigation Tabs (WCAG 2.1 AA Tablist Pattern) */}
        <div
          role="tablist"
          aria-label="Portal Navigation Tabs"
          className={`flex items-center space-x-1 p-1 rounded-xl border mb-6 overflow-x-auto ${
            highContrast ? "border-yellow-400 bg-zinc-950" : "border-gray-200 bg-white shadow-sm"
          }`}
        >
          <button
            role="tab"
            aria-selected={activeTab === "dashboard"}
            aria-controls="panel-dashboard"
            id="tab-dashboard"
            onClick={() => setActiveTab("dashboard")}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg whitespace-nowrap transition-all focus:outline-none focus-visible:ring-2 ${
              activeTab === "dashboard"
                ? highContrast
                  ? "bg-yellow-400 text-black font-extrabold"
                  : "bg-indigo-600 text-white shadow-sm"
                : highContrast
                ? "text-yellow-400 hover:bg-yellow-400/20"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            <LayoutDashboard className="w-4 h-4" aria-hidden="true" />
            <span>{t.tabDashboard}</span>
          </button>

          <button
            role="tab"
            aria-selected={activeTab === "top"}
            aria-controls="panel-top"
            id="tab-top"
            onClick={() => setActiveTab("top")}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg whitespace-nowrap transition-all focus:outline-none focus-visible:ring-2 ${
              activeTab === "top"
                ? highContrast
                  ? "bg-yellow-400 text-black font-extrabold"
                  : "bg-indigo-600 text-white shadow-sm"
                : highContrast
                ? "text-yellow-400 hover:bg-yellow-400/20"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            <Trophy className="w-4 h-4" aria-hidden="true" />
            <span>{t.tabTopSchools}</span>
          </button>

          <button
            role="tab"
            aria-selected={activeTab === "rules"}
            aria-controls="panel-rules"
            id="tab-rules"
            onClick={() => setActiveTab("rules")}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg whitespace-nowrap transition-all focus:outline-none focus-visible:ring-2 ${
              activeTab === "rules"
                ? highContrast
                  ? "bg-yellow-400 text-black font-extrabold"
                  : "bg-indigo-600 text-white shadow-sm"
                : highContrast
                ? "text-yellow-400 hover:bg-yellow-400/20"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            <Cpu className="w-4 h-4" aria-hidden="true" />
            <span>{t.tabEligibility}</span>
          </button>

          <button
            role="tab"
            aria-selected={activeTab === "dbt"}
            aria-controls="panel-dbt"
            id="tab-dbt"
            onClick={() => setActiveTab("dbt")}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg whitespace-nowrap transition-all focus:outline-none focus-visible:ring-2 ${
              activeTab === "dbt"
                ? highContrast
                  ? "bg-yellow-400 text-black font-extrabold"
                  : "bg-indigo-600 text-white shadow-sm"
                : highContrast
                ? "text-yellow-400 hover:bg-yellow-400/20"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            <CreditCard className="w-4 h-4" aria-hidden="true" />
            <span>{t.tabDisbursements}</span>
          </button>

          <button
            role="tab"
            aria-selected={activeTab === "audit"}
            aria-controls="panel-audit"
            id="tab-audit"
            onClick={() => setActiveTab("audit")}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg whitespace-nowrap transition-all focus:outline-none focus-visible:ring-2 ${
              activeTab === "audit"
                ? highContrast
                  ? "bg-yellow-400 text-black font-extrabold"
                  : "bg-indigo-600 text-white shadow-sm"
                : highContrast
                ? "text-yellow-400 hover:bg-yellow-400/20"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            <Lock className="w-4 h-4" aria-hidden="true" />
            <span>{t.tabAudit}</span>
          </button>
        </div>

        {/* Tab Panels */}
        <div className="space-y-6">
          {activeTab === "dashboard" && (
            <div id="panel-dashboard" role="tabpanel" aria-labelledby="tab-dashboard" className="space-y-6">
              <VirtualSchoolTable
                schools={schools}
                lang={lang}
                highContrast={highContrast}
                isLoading={schoolsLoading}
              />
            </div>
          )}

          {activeTab === "top" && (
            <div id="panel-top" role="tabpanel" aria-labelledby="tab-top" className="space-y-6">
              <TopSchoolsCard
                schools={topSchools}
                lang={lang}
                highContrast={highContrast}
                isLoading={topSchoolsLoading}
              />
            </div>
          )}

          {activeTab === "rules" && (
            <div id="panel-rules" role="tabpanel" aria-labelledby="tab-rules" className="space-y-6">
              <EligibilityChecker lang={lang} highContrast={highContrast} />
            </div>
          )}

          {activeTab === "dbt" && (
            <div id="panel-dbt" role="tabpanel" aria-labelledby="tab-dbt" className="space-y-6">
              <DisbursementForm lang={lang} highContrast={highContrast} />
            </div>
          )}

          {activeTab === "audit" && (
            <div id="panel-audit" role="tabpanel" aria-labelledby="tab-audit" className="space-y-6">
              <AuditVerification lang={lang} highContrast={highContrast} />
            </div>
          )}
        </div>

        {/* Assessment Architecture Summary Footer */}
        <footer
          className={`mt-12 py-6 border-t text-xs transition-colors ${
            highContrast ? "border-yellow-400/40 text-yellow-200" : "border-gray-200 text-gray-500"
          }`}
        >
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p>{t.footerText}</p>
            <div className="flex items-center gap-3">
              <span className="font-mono">FastAPI + PostgreSQL + Next.js 14</span>
              <span>•</span>
              <span className="font-semibold">{t.wcagBadge}</span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
