export type AccountStatus = "Active" | "Inactive";

/** Status values returned by the account/briefing API. */
export type ApiAccountStatus = "ACTIVE" | "INACTIVE";
export type BriefingStatus = "GENERATING" | "COMPLETED" | "FAILED" | "BLOCKED";
export type CitationSourceType = "PDF" | "COMMERCIAL";
export type CitationValidationStatus = "PENDING" | "VALID" | "INVALID" | "REJECTED";

export interface ApiSite {
  id: string;
  accountId: string;
  siteName: string;
  address: string;
}

export interface ApiAccount {
  id: string;
  legalName: string;
  taxCode: string;
  industry: string;
  status: ApiAccountStatus;
  hasPermission: boolean;
  sites?: ApiSite[];
  createdAt?: string;
  updatedAt?: string;
}

export interface Citation {
  id: string;
  briefingId: string;
  citationNumber: number;
  claimText: string;
  sourceType: CitationSourceType;
  sourceExcerpt?: string;
  validationStatus: CitationValidationStatus;
}

export interface ApiBriefing {
  id: string;
  accountId: string;
  siteId?: string | null;
  generatedBy: string;
  briefingStatus: BriefingStatus;
  isStale: boolean;
  sections: {
    companyOverview?: string;
    commercialSummary?: string;
    riskWarnings?: string[];
    recentActivities?: string[];
  };
  citations: Citation[];
  freshnessStatus: string;
  validationStatus: string;
  createdAt: string;
}

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

export type BriefingSectionKey =
  | "account_site"
  | "contacts_roles"
  | "recent_interactions"
  | "commercial_facts"
  | "service_issues"
  | "suggestions_gaps";

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

export interface BriefingCitation {
  id: string;
  label: string;
  source: string;
  is_sample: boolean;
}

export interface BriefingSection {
  key: BriefingSectionKey;
  content: string;
  citations: BriefingCitation[];
  validation_status: "verified" | "needs_review" | "not_applicable";
}

export interface BriefingContent {
  account: Account;
  site: Site;
  contacts: Contact[];
  interactions: Interaction[];
  commercial: CommercialFacts;
  service_issues: ServiceIssue[];
  suggested_questions: string[];
  information_gaps: InformationGap[];
}

export interface Briefing {
  briefing_id: string;
  account_id: string;
  status: "ready" | "draft" | "failed";
  is_stale: boolean;
  sections: BriefingSection[];
  content: BriefingContent;
  citations: BriefingCitation[];
}
