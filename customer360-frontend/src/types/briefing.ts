export type BriefingStatus = 'GENERATING' | 'COMPLETED' | 'FAILED' | 'BLOCKED';
export type ValidationStatus = 'PENDING' | 'PASSED' | 'FAILED' | 'BLOCKED';
export type CitationValidationStatus = 'PENDING' | 'VALID' | 'INVALID' | 'REJECTED';
export type SourceType = 'PDF' | 'COMMERCIAL';
export type MatchStatus = 'EXACT' | 'AMBIGUOUS' | 'SINGLE';

export interface AccountSummary {
  id: string;
  legal_name: string;
  tax_code: string | null;
  industry: string | null;
  status: 'ACTIVE' | 'INACTIVE';
  match_status: MatchStatus;
}

export interface AccountSearchResponse {
  results: AccountSummary[];
  requires_manual_selection: boolean;
}

export interface BriefingSection {
  content: string;
  citations: number[];
}

export interface BriefingSections {
  account_and_site: BriefingSection;
  contacts_and_roles: BriefingSection;
  recent_interactions: BriefingSection;
  commercial_facts: BriefingSection;
  service_issues: BriefingSection;
  suggested_questions_and_gaps: BriefingSection;
}

export interface BriefingResponse {
  briefing_id: string;
  account_id: string;
  site_id: string | null;
  status: BriefingStatus;
  is_stale: boolean;
  sections: BriefingSections;
  validation_status: ValidationStatus;
  created_at: string;
  completed_at: string | null;
}

export interface BriefingAcceptedResponse {
  briefing_id: string;
  status: 'GENERATING';
  message: string;
}

export interface CitationItem {
  citation_number: number;
  claim_text: string;
  source_type: SourceType;
  source_id: string;
  page_number: number | null;
  source_excerpt: string | null;
  validation_status: CitationValidationStatus;
}

export interface BriefingCitationsResponse {
  briefing_id: string;
  citations: CitationItem[];
}

export type CitationMap = Record<number, CitationItem>;
