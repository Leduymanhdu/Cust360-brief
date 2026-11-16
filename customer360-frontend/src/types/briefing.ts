// ============================================================
// briefing.ts – Type definitions for Briefing & Citations
// KAN-20: Citation Tooltip UI Component
// ============================================================

export type SourceType = 'PDF' | 'COMMERCIAL';

export type ValidationStatus = 'PENDING' | 'VALID' | 'INVALID' | 'REJECTED';

/**
 * Một trích dẫn (citation) trả về từ API GET /briefings/{id}/citations
 * Căn cứ: SDS Mục 3.3 – FR-BRF-003
 */
export interface Citation {
  id: string;
  briefing_id: string;
  citation_number: number;
  claim_text: string;
  source_type: SourceType;
  /** Tên file nguồn (PDF) hoặc tên hệ thống thương mại (COMMERCIAL) */
  source_name: string;
  /** Chỉ có khi source_type === 'PDF' */
  page_number?: number;
  /** Đoạn trích nguyên văn từ nguồn */
  source_excerpt?: string;
  validation_status: ValidationStatus;
}

/**
 * Map nhanh: citation_number → Citation
 * Dùng trong BriefingView để lookup O(1)
 */
export type CitationMap = Record<number, Citation>;

/**
 * Một câu khẳng định trong Briefing có thể chứa nhiều citation numbers
 */
export interface BriefingStatement {
  text: string;
  citation_numbers: number[];
}

/**
 * Một section trong Briefing (vd: "Tổng quan khách hàng", "Thương mại", ...)
 */
export interface BriefingSection {
  title: string;
  statements: BriefingStatement[];
}

/**
 * Briefing đầy đủ
 */
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

/**
 * Response từ API GET /briefings/{id}/citations
 */
export interface CitationsResponse {
  briefing_id: string;
  citations: Citation[];
}
