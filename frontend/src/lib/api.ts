/**
 * API Client Configuration
 * Connects Next.js frontend to FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchSchools(district?: string, search?: string, limit = 1200) {
  const params = new URLSearchParams();
  if (district) params.append("district", district);
  if (search) params.append("search", search);
  params.append("limit", limit.toString());

  const res = await fetch(`${API_BASE_URL}/schools?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch school registry");
  return res.json();
}

export async function fetchTopSchools() {
  const res = await fetch(`${API_BASE_URL}/schools/top-enrollment`);
  if (!res.ok) throw new Error("Failed to fetch top schools");
  return res.json();
}

export async function evaluateApplication(data: {
  family_income: number;
  attendance_percentage: number;
  marks_percentage: number;
  district: string;
  category: string;
}) {
  const res = await fetch(`${API_BASE_URL}/eligibility/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to evaluate eligibility");
  return res.json();
}

export async function executeDisbursement(
  data: { student_id: number; scheme_code: string; amount: number },
  idempotencyKey: string
) {
  const res = await fetch(`${API_BASE_URL}/disbursements`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify(data),
  });

  const isReplay = res.headers.get("Idempotent-Replay") === "true";
  const json = await res.json();
  return { ...json, is_idempotent_replay: isReplay || json.is_idempotent_replay };
}

export async function verifyAuditLedger(adminToken: string) {
  const res = await fetch(`${API_BASE_URL}/audit/verify`, {
    headers: { Authorization: `Bearer ${adminToken}` },
  });
  if (!res.ok) throw new Error("Audit verification failed");
  return res.json();
}

export async function getDemoToken(role: string, district?: string, student_id?: number) {
  const res = await fetch(`${API_BASE_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role, district, student_id }),
  });
  if (!res.ok) throw new Error("Failed to generate token");
  return res.json();
}
