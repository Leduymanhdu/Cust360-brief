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
