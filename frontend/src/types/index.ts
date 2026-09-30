export interface School {
  id: number;
  school_name: string;
  district: string;
  total_students: number;
  udise_code?: string;
}

export interface TopSchool {
  id: number;
  school_name: string;
  district: string;
  total_students: number;
}

export interface RuleEvaluationItem {
  rule_name: string;
  passed: boolean;
  message: string;
  threshold?: string;
  actual_value?: string;
}

export interface ApplicationEvaluationResponse {
  is_eligible: boolean;
  scheme_name: string;
  rules_evaluated: RuleEvaluationItem[];
  disqualification_reasons: string[];
  rule_version: string;
  evaluated_at: string;
}

export interface DisbursementResponse {
  disbursement_reference: string;
  idempotency_key: string;
  student_id: number;
  scheme_code: string;
  amount: number;
  status: string;
  payment_gateway_txn_id?: string;
  executed_at: string;
  is_idempotent_replay: boolean;
}

export interface AuditVerificationResponse {
  is_valid: boolean;
  total_records: number;
  status: string;
  message: string;
  latest_record_hash?: string;
  tampered_record_id?: number;
  reason?: string;
}

export type Language = "en" | "gu";
