export type SourceType = 'PDF' | 'COMMERCIAL';

export type ValidationStatus = 'PENDING' | 'VALID' | 'INVALID' | 'REJECTED';

export interface Citation {
  id: string;
  briefing_id: string;
  citation_number: number;
  claim_text: string;
  source_type: SourceType;
  source_name: string;
  page_number?: number;
  source_excerpt?: string;
  validation_status: ValidationStatus;
}

export type CitationMap = Record<number, Citation>;

export interface BriefingStatement {
  text: string;
  citation_numbers: number[];
}

export interface BriefingSection {
  title: string;
  statements: BriefingStatement[];
}

export interface Briefing {
  id: string;
  account_id: string;
  site_id?: string;
  generated_by: string;
  briefing_status: 'GENERATING' | 'COMPLETED' | 'FAILED' | 'BLOCKED';
  sections: BriefingSection[];
  is_stale: boolean;
  validation_status: ValidationStatus;
  created_at: string;
  completed_at?: string;
}

export interface CitationsResponse {
  briefing_id: string;
  citations: Citation[];
}
