import type { InformationGap } from "../../types/briefing";
import { SectionHeading } from "./BriefingPrimitives";

interface SuggestedQuestionsCardProps {
  questions: string[];
  gaps: InformationGap[];
}

const gapLabel: Record<InformationGap["state"], string> = {
  Missing: "Missing",
  Inconsistent: "Inconsistent",
  Unverified: "Needs verification",
};

export function SuggestedQuestionsCard({
  questions,
  gaps,
}: SuggestedQuestionsCardProps) {
  return (
    <section aria-labelledby="follow-up-title" className="card">
      <SectionHeading
        description="Meeting prompts and customer details to confirm."
        eyebrow="PREPARATION"
        title="Suggested Questions & Information Gaps"
        titleId="follow-up-title"
      />
      <div className="follow-up-grid">
        <div className="follow-up-panel">
          <div className="panel-heading">
            <span aria-hidden="true" className="panel-icon question-icon">
              ?
            </span>
            <div>
              <h3>Suggested Questions</h3>
              <p>Discussion prompts for the next customer meeting.</p>
            </div>
          </div>
          <ol className="question-list">
            {questions.map((question, index) => (
              <li key={question}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{question}</p>
              </li>
            ))}
          </ol>
        </div>
        <div className="follow-up-panel gaps-panel">
          <div className="panel-heading">
            <span aria-hidden="true" className="panel-icon gap-icon">
              !
            </span>
            <div>
              <h3>Information Gaps</h3>
              <p>Items requiring confirmation or follow-up.</p>
            </div>
          </div>
          <div className="gap-list">
            {gaps.map((gap) => (
              <article className="gap-item" key={gap.id}>
                <div className="gap-title-line">
                  <h4>{gap.title}</h4>
                  <span
                    className={`gap-state gap-${gap.state.toLowerCase()}`}
                  >
                    {gapLabel[gap.state]}
                  </span>
                </div>
                <p>{gap.description}</p>
                <p className="follow-up-action">
                  <strong>Follow up:</strong> {gap.follow_up_action}
                </p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
