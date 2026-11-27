export type AccountStatus = "Active" | "Inactive";

/** Status values returned by the account/briefing API. */
export type ApiAccountStatus = "ACTIVE" | "INACTIVE";
export type BriefingStatus = "GENERATING" | "COMPLETED" | "FAILED" | "BLOCKED";
export type CitationSourceType = "PDF" | "COMMERCIAL";
export type CitationValidationStatus = "PENDING" | "VALID" | "INVALID" | "REJECTED";

/** Citation tooltip API model (snake_case response fields). */
export type SourceType = CitationSourceType;
export type ValidationStatus = CitationValidationStatus;

export interface TooltipCitation {
  briefing_id?: string;
  citation_number: number;
  claim_text: string;
  source_type: SourceType;
  source_id: string;
  source_name?: string;
  page_number?: number | null;
  source_excerpt?: string | null;
  validation_status: ValidationStatus;
}

export type CitationMap = Record<number, TooltipCitation>;

export interface CitationsResponse {
  briefing_id: string;
  citations: TooltipCitation[];
}

export interface ApiBriefingSection {
  content: string;
  citations: number[];
}

export type ApiBriefingSectionKey =
  | "account_and_site"
  | "contacts_and_roles"
  | "recent_interactions"
  | "commercial_facts"
  | "service_issues"
  | "suggested_questions_and_gaps";

export interface ApiBriefingResponse {
  briefing_id: string;
  account_id: string;
  site_id: string | null;
  status: BriefingStatus;
  is_stale: boolean;
  sections: Record<ApiBriefingSectionKey, ApiBriefingSection>;
  validation_status: "PENDING" | "PASSED" | "FAILED" | "BLOCKED";
  created_at: string;
  completed_at: string | null;
}

export interface ApiSite {
  id: string;
  site_name: string;
  address: string | null;
}

export interface ApiAccount {
  id: string;
  legal_name: string;
  tax_code: string | null;
  industry: string | null;
  status: ApiAccountStatus;
  sites?: ApiSite[];
  match_status?: "EXACT" | "AMBIGUOUS" | "SINGLE";
}

export type Citation = TooltipCitation;

export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resourceType: string;
  resourceId: string;
  ipAddress?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
}

export type InteractionType =
  | "Meeting"
  | "Call"
  | "Email"
  | "Site visit";

export type QuotationStatus = "Pending" | "Approved" | "Rejected";

export type ServicePriority = "Critical" | "High" | "Medium" | "Low";

export type ServiceIssueStatus =
  | "Open"
  | "In Progress"
  | "Resolved"
  | "Closed";

export interface Account {
  id: string;
  name: string;
  type: string;
  status: AccountStatus;
  industry: string;
  owner: string;
}

export interface Site {
  name: string;
  address: string;
  location: string;
  last_updated: string;
}

export interface Contact {
  id: string;
  full_name: string;
  job_title: string;
  department: string;
  email: string;
  phone: string;
  role: string;
  is_primary: boolean;
}

export interface Interaction {
  id: string;
  type: InteractionType;
  date: string;
  subject: string;
  description: string;
  related_contact: string;
  responsible_employee: string;
  status: string;
}

export interface CommercialRecord {
  id: string;
  kind: "Quotation" | "Sale";
  reference: string;
  description: string;
  date: string;
  amount: number;
  currency: string;
  status: QuotationStatus | "Completed";
}

export interface CommercialFacts {
  currency: string;
  total_sales_revenue: number;
  total_quotation_value: number;
  quotation_count: number;
  pending_quotations: number;
  approved_quotations: number;
  records: CommercialRecord[];
}

export interface ServiceIssue {
  id: string;
  title: string;
  description: string;
  priority: ServicePriority;
  status: ServiceIssueStatus;
  created_at: string;
  assigned_employee: string;
  resolution_deadline: string;
}

export interface InformationGap {
  id: string;
  title: string;
  description: string;
  state: "Missing" | "Inconsistent" | "Unverified";
  follow_up_action: string;
}
