"use client";

import React, { useState } from "react";
import { ShieldCheck, Lock, CheckCircle2, AlertOctagon } from "lucide-react";
import { AuditVerificationResponse, Language } from "@/types";
import { translations } from "@/lib/i18n";
import { verifyAuditLedger, getDemoToken } from "@/lib/api";

interface AuditVerificationProps {
  lang: Language;
  highContrast: boolean;
}

export default function AuditVerification({ lang, highContrast }: AuditVerificationProps) {
  const t = translations[lang];

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AuditVerificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Obtain State Admin Token
      const tokenData = await getDemoToken("STATE_ADMIN");
      // 2. Execute verification
      const verifyData = await verifyAuditLedger(tokenData.access_token);
      setResult(verifyData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to complete audit ledger verification";
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
            <Lock className="w-5 h-5 text-indigo-600" aria-hidden="true" />
            <h2 className="text-lg font-bold">{t.auditHeading}</h2>
          </div>
          <p
            className={`text-xs mt-1 ${
              highContrast ? "text-yellow-200" : "text-gray-500"
            }`}
          >
            {t.auditDescription}
          </p>
        </div>

        <div
          className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-semibold ${
            highContrast
              ? "border border-yellow-400 text-yellow-400"
              : "bg-indigo-50 text-indigo-800 border border-indigo-200"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Blockchain Chaining (Q11)</span>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-4">
        <button
          type="button"
          onClick={handleVerify}
          disabled={loading}
          className={`py-2 px-4 text-xs font-bold rounded-lg transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
            highContrast
              ? "bg-yellow-400 text-black hover:bg-yellow-300 focus-visible:ring-yellow-400 font-extrabold"
              : "bg-indigo-600 text-white hover:bg-indigo-700 focus-visible:ring-indigo-600 shadow-sm"
          }`}
        >
          {loading ? t.verifyingChain : t.btnVerifyChain}
        </button>
      </div>

      {error && (
        <div className="p-3 mb-4 rounded-lg bg-red-50 text-red-700 text-xs border border-red-200">
          {error}
        </div>
      )}

      {result && (
        <div
          className={`p-4 rounded-xl border ${
            result.is_valid
              ? highContrast
                ? "border-yellow-400 bg-zinc-950"
                : "border-emerald-200 bg-emerald-50/50"
              : highContrast
              ? "border-red-500 bg-zinc-950"
              : "border-red-200 bg-red-50/50"
          }`}
          role="region"
          aria-live="polite"
        >
          <div className="flex items-center gap-2 mb-2">
            {result.is_valid ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" aria-hidden="true" />
            ) : (
              <AlertOctagon className="w-5 h-5 text-red-600 shrink-0" aria-hidden="true" />
            )}
            <h3 className="text-xs font-bold uppercase tracking-wider">
              {result.is_valid ? "Cryptographic Ledger Verified" : "Tampering Detected"}
            </h3>
          </div>

          <p className="text-xs mb-3">
            {result.is_valid ? t.chainValid : `${t.chainCompromised} ${result.tampered_record_id}`}
          </p>

          <div className="p-3 rounded-lg bg-black/5 dark:bg-white/5 space-y-1.5 font-mono text-[11px]">
            <div className="flex justify-between">
              <span className="text-gray-400">{t.totalAuditRecords}:</span>
              <span className="font-bold">{result.total_records}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Ledger Status:</span>
              <span className="font-bold text-emerald-600">{result.status}</span>
            </div>
            {result.latest_record_hash && (
              <div className="pt-1 border-t border-gray-200/40">
                <span className="text-gray-400 block text-[10px]">Head Record Hash:</span>
                <span className="font-bold text-[10px] break-all">{result.latest_record_hash}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
