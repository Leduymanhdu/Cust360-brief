import type { ServiceIssue } from "../../types/briefing";
import { SectionHeading, StatusBadge } from "./BriefingPrimitives";

export function ServiceIssuesCard({
  issues,
}: {
  issues: ServiceIssue[];
}) {
  const unresolvedCount = issues.filter(
    (issue) => issue.status === "Open" || issue.status === "In Progress",
  ).length;

  return (
    <section aria-labelledby="service-issues-title" className="card">
      <SectionHeading
        description="Tickets needing attention and recently completed work."
        eyebrow="SUPPORT"
        title="Service Issues"
        titleId="service-issues-title"
        trailing={
          <span className="count-pill count-pill-warning">
            {unresolvedCount} unresolved
          </span>
        }
      />
      <div className="issue-list">
        {issues.map((issue) => (
          <article className="issue-row" key={issue.id}>
            <div className="issue-main">
              <div className="issue-title-line">
                <span className="ticket-id">{issue.id}</span>
                <span
                  className={`priority-label priority-${issue.priority.toLowerCase()}`}
                >
                  {issue.priority} priority
                </span>
              </div>
              <h3>{issue.title}</h3>
              <p>{issue.description}</p>
              <div className="issue-meta">
                <span>Assigned to {issue.assigned_employee}</span>
                <span>
                  Due{" "}
                  <time dateTime={issue.resolution_deadline}>
                    {new Intl.DateTimeFormat("en", {
                      dateStyle: "medium",
                    }).format(new Date(`${issue.resolution_deadline}T00:00:00`))}
                  </time>
                </span>
                <span>
                  Created{" "}
                  <time dateTime={issue.created_at}>
                    {new Intl.DateTimeFormat("en", {
                      dateStyle: "medium",
                    }).format(new Date(`${issue.created_at}T00:00:00`))}
                  </time>
                </span>
              </div>
            </div>
            <StatusBadge value={issue.status} />
          </article>
        ))}
      </div>
    </section>
  );
}
