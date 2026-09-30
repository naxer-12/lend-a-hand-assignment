"use client";

import React, { useState } from "react";
import { CreditCard, Repeat, RefreshCw, CheckCircle2, ShieldAlert, Key } from "lucide-react";
import { DisbursementResponse, Language } from "@/types";
import { translations } from "@/lib/i18n";
import { executeDisbursement } from "@/lib/api";

interface DisbursementFormProps {
  lang: Language;
  highContrast: boolean;
}

function generateUUID(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export default function DisbursementForm({ lang, highContrast }: DisbursementFormProps) {
  const t = translations[lang];

  const [studentId, setStudentId] = useState("1");
  const [schemeCode, setSchemeCode] = useState("GJ-MYSY-2026");
  const [amount, setAmount] = useState("25000");
  const [idempotencyKey, setIdempotencyKey] = useState<string>(generateUUID());

  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<DisbursementResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePay = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await executeDisbursement(
        {
          student_id: parseInt(studentId, 10),
          scheme_code: schemeCode,
          amount: parseFloat(amount),
        },
        idempotencyKey
      );
      setResponse(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Disbursement failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateKey = () => {
    setIdempotencyKey(generateUUID());
    setResponse(null);
    setError(null);
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
            <CreditCard className="w-5 h-5 text-emerald-600" aria-hidden="true" />
            <h2 className="text-lg font-bold">{t.disbursementHeading}</h2>
          </div>
          <p
            className={`text-xs mt-1 ${
              highContrast ? "text-yellow-200" : "text-gray-500"
            }`}
          >
            {t.disbursementDescription}
          </p>
        </div>

        <div
          className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-semibold ${
            highContrast
              ? "border border-yellow-400 text-yellow-400"
              : "bg-emerald-50 text-emerald-800 border border-emerald-200"
          }`}
        >
          <Repeat className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Idempotent API (Q2)</span>
        </div>
      </div>

      {/* Idempotency Key Bar */}
      <div
        className={`flex flex-col sm:flex-row items-stretch sm:items-center justify-between p-3 rounded-lg border gap-2 mb-4 ${
          highContrast ? "border-yellow-400 bg-zinc-950" : "border-gray-200 bg-gray-50/80"
        }`}
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <Key className="w-4 h-4 text-indigo-600 shrink-0" aria-hidden="true" />
          <div className="truncate">
            <span className="text-[10px] uppercase font-bold text-gray-400 block">
              {t.labelIdempotencyKey}
            </span>
            <span className="text-xs font-mono font-bold tracking-tight truncate block">
              {idempotencyKey}
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={handleRegenerateKey}
          className={`inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded border transition-all shrink-0 ${
            highContrast
              ? "border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black"
              : "border-gray-300 bg-white text-gray-700 hover:bg-gray-100 shadow-sm"
          }`}
        >
          <RefreshCw className="w-3 h-3" />
          <span>{t.btnGenerateKey}</span>
        </button>
      </div>

      {/* Form Fields */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelStudentId}</label>
          <input
            type="number"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelSchemeCode}</label>
          <input
            type="text"
            value={schemeCode}
            onChange={(e) => setSchemeCode(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1">{t.labelAmount}</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className={`w-full px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus-visible:ring-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <button
          type="button"
          onClick={handlePay}
          disabled={loading}
          className={`flex-1 py-2 px-4 text-xs font-bold rounded-lg transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
            highContrast
              ? "bg-yellow-400 text-black hover:bg-yellow-300 focus-visible:ring-yellow-400 font-extrabold"
              : "bg-emerald-600 text-white hover:bg-emerald-700 focus-visible:ring-emerald-600 shadow-sm"
          }`}
        >
          {loading ? "Executing Payment..." : t.btnPay}
        </button>

        <button
          type="button"
          onClick={handlePay}
          disabled={loading}
          className={`flex-1 py-2 px-4 text-xs font-bold rounded-lg border transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
            highContrast
              ? "border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black"
              : "border-indigo-300 bg-indigo-50 text-indigo-700 hover:bg-indigo-100"
          }`}
        >
          <span className="flex items-center justify-center gap-1.5">
            <Repeat className="w-3.5 h-3.5" />
            {t.btnRetry}
          </span>
        </button>
      </div>

      {error && (
        <div className="p-3 mb-4 rounded-lg bg-red-50 text-red-700 text-xs border border-red-200">
          {error}
        </div>
      )}

      {/* Response Box with Idempotent Replay Indicator */}
      {response && (
        <div
          className={`p-4 rounded-xl border ${
            response.is_idempotent_replay
              ? highContrast
                ? "border-yellow-400 bg-zinc-950"
                : "border-blue-300 bg-blue-50/50"
              : highContrast
              ? "border-emerald-400 bg-zinc-950"
              : "border-emerald-200 bg-emerald-50/50"
          }`}
          role="region"
          aria-live="polite"
        >
          <div className="flex items-center gap-2 mb-2">
            {response.is_idempotent_replay ? (
              <ShieldAlert className="w-5 h-5 text-blue-600 shrink-0" aria-hidden="true" />
            ) : (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" aria-hidden="true" />
            )}
            <h3 className="text-xs font-bold uppercase tracking-wider">
              {response.is_idempotent_replay ? "Idempotent Replay" : "Authoritative New Execution"}
            </h3>
          </div>

          <p className="text-xs mb-3">
            {response.is_idempotent_replay ? t.replayNotice : t.newPaymentSuccess}
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] font-mono p-2.5 rounded bg-black/5 dark:bg-white/5">
            <div>
              <span className="text-gray-400 block">Ref:</span>
              <span className="font-bold">{response.disbursement_reference}</span>
            </div>
            <div>
              <span className="text-gray-400 block">Amount:</span>
              <span className="font-bold">₹{response.amount.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-gray-400 block">Status:</span>
              <span className="text-emerald-600 font-bold">{response.status}</span>
            </div>
            <div>
              <span className="text-gray-400 block">Header Replay:</span>
              <span className="font-bold text-blue-600">
                {response.is_idempotent_replay ? "true" : "false"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
