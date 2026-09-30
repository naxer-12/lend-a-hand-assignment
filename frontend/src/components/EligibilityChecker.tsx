"use client";

import React, { useState } from "react";
import { CheckCircle2, XCircle, Award, Cpu } from "lucide-react";
import { ApplicationEvaluationResponse, Language } from "@/types";
import { translations } from "@/lib/i18n";
import { evaluateApplication } from "@/lib/api";

interface EligibilityCheckerProps {
  lang: Language;
  highContrast: boolean;
}

export default function EligibilityChecker({ lang, highContrast }: EligibilityCheckerProps) {
  const t = translations[lang];

  const [income, setIncome] = useState("240000");
  const [attendance, setAttendance] = useState("82.5");
  const [marks, setMarks] = useState("76.0");
  const [category, setCategory] = useState("GENERAL");
  const [district, setDistrict] = useState("Gandhinagar");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ApplicationEvaluationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await evaluateApplication({
        family_income: parseFloat(income) || 0,
        attendance_percentage: parseFloat(attendance) || 0,
        marks_percentage: parseFloat(marks) || 0,
        category,
        district,
      });
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to contact eligibility rule engine";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

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
            <Cpu className="w-5 h-5 text-indigo-600" aria-hidden="true" />
            <h2 className="text-lg font-bold">{t.eligibilityHeading}</h2>
          </div>
          <p
            className={`text-xs mt-1 ${
              highContrast ? "text-yellow-200" : "text-gray-500"
            }`}
          >
            {t.eligibilityDescription}
          </p>
        </div>

        <div
          className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-semibold ${
            highContrast
              ? "border border-yellow-400 text-yellow-400"
              : "bg-indigo-50 text-indigo-800 border border-indigo-200"
          }`}
        >
          <Award className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Strategy Pattern (Q6)</span>
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleEvaluate} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 mb-6">
        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelFamilyIncome}</label>
          <input
            type="number"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelAttendance}</label>
          <input
            type="number"
            step="0.1"
            value={attendance}
            onChange={(e) => setAttendance(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelMarks}</label>
          <input
            type="number"
            step="0.1"
            value={marks}
            onChange={(e) => setMarks(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelCategory}</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
          >
            <option value="GENERAL">General</option>
            <option value="OBC">OBC (65% cutoff)</option>
            <option value="SC">SC (55% cutoff)</option>
            <option value="ST">ST (55% cutoff)</option>
            <option value="EWS">EWS (70% cutoff)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelDistrict}</label>
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
          >
            <option value="Gandhinagar">Gandhinagar</option>
            <option value="Ahmedabad">Ahmedabad</option>
            <option value="Surat">Surat</option>
            <option value="Vadodara">Vadodara</option>
            <option value="Rajkot">Rajkot</option>
            <option value="Bhavnagar">Bhavnagar</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-1.5 px-3 text-xs font-bold rounded-lg transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
              highContrast
                ? "bg-yellow-400 text-black hover:bg-yellow-300 focus-visible:ring-yellow-400 font-extrabold"
                : "bg-indigo-600 text-white hover:bg-indigo-700 focus-visible:ring-indigo-600 shadow-sm"
            }`}
          >
            {loading ? t.evaluating : t.btnCheckEligibility}
          </button>
        </div>
      </form>

      {error && (
        <div className="p-3 mb-4 rounded-lg bg-red-50 text-red-700 text-xs border border-red-200">
          {error}
        </div>
      )}

      {/* Evaluation Results Breakdown */}
      {result && (
        <div
          className={`p-4 rounded-xl border ${
            result.is_eligible
              ? highContrast
                ? "border-yellow-400 bg-zinc-950"
                : "border-emerald-200 bg-emerald-50/40"
              : highContrast
              ? "border-red-500 bg-zinc-950"
              : "border-amber-200 bg-amber-50/40"
          }`}
          role="region"
          aria-live="polite"
        >
          {/* Main Verdict Banner */}
          <div className="flex items-center gap-2 mb-3">
            {result.is_eligible ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" aria-hidden="true" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600 shrink-0" aria-hidden="true" />
            )}
            <div>
              <h3 className="text-sm font-bold">
                {result.is_eligible ? t.eligibleSuccess : t.disqualifiedWarning}
              </h3>
              <p className="text-[11px] text-gray-500">
                Scheme: {result.scheme_name} (Rule Version: {result.rule_version})
              </p>
            </div>
          </div>

          {/* Individual Rule Evaluation Results */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 pt-3 border-t border-gray-200/40">
            {result.rules_evaluated.map((r, i) => (
              <div
                key={i}
                className={`p-2.5 rounded-lg border text-xs flex items-start justify-between gap-2 ${
                  r.passed
                    ? highContrast
                      ? "border-yellow-400/40 bg-black"
                      : "border-emerald-200 bg-white"
                    : highContrast
                    ? "border-red-400 bg-black"
                    : "border-red-200 bg-white"
                }`}
              >
                <div>
                  <div className="font-semibold">{r.rule_name}</div>
                  <div className="text-[11px] text-gray-500 mt-0.5">{r.message}</div>
                  {r.threshold && (
                    <div className="text-[10px] text-gray-400 font-mono mt-1">
                      Req: {r.threshold} | Actual: {r.actual_value}
                    </div>
                  )}
                </div>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-bold shrink-0 ${
                    r.passed
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {r.passed ? "PASS" : "FAIL"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
