import React from 'react';
import type { BriefingResponse, CitationMap } from '../../types/briefing';
import { CitationBadge } from '../citation/CitationBadge';

const SECTION_LABELS: Record<keyof BriefingResponse['sections'], string> = {
  account_and_site: '🏢 Tổng quan tài khoản & địa điểm',
  contacts_and_roles: '👥 Liên hệ & vai trò',
  recent_interactions: '🗓 Tương tác gần đây',
  commercial_facts: '💰 Dữ liệu thương mại',
  service_issues: '🔧 Vấn đề dịch vụ',
  suggested_questions_and_gaps: '❓ Câu hỏi đề xuất & khoảng trống dữ liệu',
};

interface BriefingViewProps {
  briefing: BriefingResponse;
  citationMap: CitationMap;
  isLoadingCitations: boolean;
}

export const BriefingView: React.FC<BriefingViewProps> = ({
  briefing,
  citationMap,
  isLoadingCitations,
}) => {
  const sectionKeys = Object.keys(SECTION_LABELS) as Array<
    keyof BriefingResponse['sections']
  >;

  return (
    <div style={s.wrapper}>
      {sectionKeys.map((key) => {
        const section = briefing.sections[key];
        const hasContent = section?.content?.trim();

        return (
          <div key={key} style={s.section}>
            <h3 style={s.sectionTitle}>{SECTION_LABELS[key]}</h3>

            {!hasContent ? (
              <p style={s.emptyText}>Không có dữ liệu cho mục này.</p>
            ) : (
              <p style={s.content}>
                <span>{section.content}</span>
                {section.citations.map((num) => (
                  <CitationBadge
                    key={num}
                    citationNumber={num}
                    citation={citationMap[num]}
                    isLoading={isLoadingCitations}
                  />
                ))}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};

const s: Record<string, React.CSSProperties> = {
  wrapper: { display: 'flex', flexDirection: 'column', gap: 0 },
  section: {
    padding: '18px 0',
    borderBottom: '1px solid #f1f3f4',
  },
  sectionTitle: {
    margin: '0 0 8px',
    fontSize: '0.9rem',
    fontWeight: 700,
    color: '#3c4043',
    textTransform: 'uppercase',
    letterSpacing: '0.03em',
  },
  content: {
    margin: 0,
    fontSize: '0.9rem',
    lineHeight: 1.65,
    color: '#202124',
  },
  emptyText: {
    margin: 0,
    fontSize: '0.85rem',
    color: '#9aa0a6',
    fontStyle: 'italic',
  },
};

export default BriefingView;
