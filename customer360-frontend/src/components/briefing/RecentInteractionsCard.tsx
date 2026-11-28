import type { Interaction } from "../../types/briefing";
import { SectionHeading, StatusBadge } from "./BriefingPrimitives";

const interactionClass = (type: Interaction["type"]) =>
  `interaction-${type.toLowerCase().replace(/\s+/g, "-")}`;

export function RecentInteractionsCard({
  interactions,
}: {
  interactions: Interaction[];
}) {
  const newestFirst = [...interactions].sort(
    (first, second) =>
      new Date(second.date).getTime() - new Date(first.date).getTime(),
  );

  return (
    <section aria-labelledby="interactions-title" className="card">
      <SectionHeading
        description="A chronological view of recent customer activity."
        eyebrow="ACTIVITY"
        title="Recent Interactions"
        titleId="interactions-title"
        trailing={<span className="count-pill">{interactions.length} records</span>}
      />
      <ol className="interaction-timeline">
        {newestFirst.map((interaction) => (
          <li className="interaction-item" key={interaction.id}>
            <span
              aria-hidden="true"
              className={`interaction-marker ${interactionClass(interaction.type)}`}
            />
            <article className="interaction-content">
              <div className="interaction-meta">
                <span
                  className={`interaction-type ${interactionClass(interaction.type)}`}
                >
                  {interaction.type}
                </span>
                <time dateTime={interaction.date}>
                  {new Intl.DateTimeFormat("en", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  }).format(new Date(interaction.date))}
                </time>
              </div>
              <div className="interaction-title-line">
                <h3>{interaction.subject}</h3>
                <StatusBadge value={interaction.status} />
              </div>
              <p>{interaction.description}</p>
              <div className="interaction-footer">
                <span>Contact: {interaction.related_contact}</span>
                <span>Owner: {interaction.responsible_employee}</span>
              </div>
            </article>
          </li>
        ))}
      </ol>
    </section>
  );
}
