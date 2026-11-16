// ============================================================
// BriefingStatement.tsx
// KAN-20 – Render một câu khẳng định kèm các citation badges [n]
//
// Dùng trong BriefingView để hiển thị từng câu có trích dẫn.
// ============================================================

import React from 'react';
import type { CitationMap } from '../../types/briefing';
import { CitationBadge } from './CitationBadge';
import styles from './BriefingStatement.module.css';

interface BriefingStatementProps {
  text: string;
  citationNumbers: number[];
  citationMap: CitationMap;
  isLoadingCitations: boolean;
}

/**
 * Hiển thị một câu khẳng định, theo sau là các badge [1] [2] ...
 * mỗi badge khi hover sẽ show tooltip với chi tiết trích dẫn.
 */
export const BriefingStatement: React.FC<BriefingStatementProps> = ({
  text,
  citationNumbers,
  citationMap,
  isLoadingCitations,
}) => {
  return (
    <p className={styles.statement}>
      <span className={styles.statementText}>{text}</span>
      {citationNumbers.map((num) => (
        <CitationBadge
          key={num}
          citationNumber={num}
          citation={citationMap[num]}
          isLoading={isLoadingCitations}
        />
      ))}
    </p>
  );
};

export default BriefingStatement;
