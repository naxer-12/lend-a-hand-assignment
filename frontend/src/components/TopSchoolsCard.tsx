"use client";

import React from "react";
import { Trophy, Database } from "lucide-react";
import { TopSchool, Language } from "@/types";
import { translations } from "@/lib/i18n";

interface TopSchoolsCardProps {
  schools: TopSchool[];
  lang: Language;
  highContrast: boolean;
  isLoading: boolean;
}

export default function TopSchoolsCard({
  schools,
  lang,
  highContrast,
  isLoading,
}: TopSchoolsCardProps) {
  const t = translations[lang];

  return (
    <div
      className={`rounded-xl border shadow-sm p-4 sm:p-6 transition-colors ${
        highContrast
          ? "bg-black border-yellow-400 text-yellow-400"
          : "bg-white border-gray-200 text-gray-900"
      }`}
    >
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-500" aria-hidden="true" />
            <h2 className="text-lg font-bold">{t.topSchoolsHeading}</h2>
          </div>
          <p
            className={`text-xs mt-1 font-mono ${
              highContrast ? "text-yellow-200" : "text-gray-500"
            }`}
          >
            {t.topSchoolsDescription}
          </p>
        </div>

        <div
          className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-semibold ${
            highContrast
              ? "border border-yellow-400 text-yellow-400"
              : "bg-amber-50 text-amber-800 border border-amber-200"
          }`}
        >
          <Database className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Raw SQL (Q4)</span>
        </div>
      </div>

      {isLoading ? (
        <div className="py-8 text-center text-xs text-gray-500 animate-pulse">
          Querying optimized index (idx_schools_total_students_desc)...
        </div>
      ) : (
        <div className="space-y-3">
          {schools.slice(0, 5).map((school, index) => {
            const rank = index + 1;
            const rankColors = [
              "bg-amber-500 text-white", // 1st
              "bg-slate-400 text-white", // 2nd
              "bg-amber-700 text-white", // 3rd
              "bg-indigo-600 text-white", // 4th
              "bg-indigo-500 text-white", // 5th
            ];

            return (
              <div
                key={school.id}
                className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
                  highContrast
                    ? "border-yellow-400/60 bg-zinc-950"
                    : "border-gray-100 bg-gray-50/50 hover:bg-indigo-50/30"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                      highContrast
                        ? "bg-yellow-400 text-black border border-black font-extrabold"
                        : rankColors[index] || "bg-gray-400 text-white"
                    }`}
                    aria-label={`Rank ${rank}`}
                  >
                    {rank}
                  </div>
                  <div>
                    <h3 className="text-xs font-bold truncate max-w-xs sm:max-w-md">
                      {school.school_name}
                    </h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded font-medium ${
                          highContrast
                            ? "text-yellow-300"
                            : "text-gray-500 bg-gray-200/60"
                        }`}
                      >
                        {school.district}
                      </span>
                      <span className="text-[10px] text-gray-400">ID #{school.id}</span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-sm font-bold font-mono">
                    {school.total_students.toLocaleString()}
                  </span>
                  <span
                    className={`block text-[10px] ${
                      highContrast ? "text-yellow-200" : "text-gray-400"
                    }`}
                  >
                    Students
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
