import type { ReactNode } from "react";

export interface SectionHeadingProps {
  eyebrow: string;
  title: string;
  description?: string;
  titleId?: string;
  trailing?: ReactNode;
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  titleId,
  trailing,
}: SectionHeadingProps) {
  return (
    <div className="section-heading">
      <div>
        <p className="section-eyebrow">{eyebrow}</p>
        <h2 id={titleId}>{title}</h2>
        {description ? <p className="section-description">{description}</p> : null}
      </div>
      {trailing ? <div className="section-trailing">{trailing}</div> : null}
    </div>
  );
}

export function StatusBadge({ value }: { value: string }) {
  const tone = value.toLowerCase().replace(/\s+/g, "-");
  return <span className={`status-badge status-${tone}`}>{value}</span>;
}

export function ContactIcon({ kind }: { kind: "email" | "phone" }) {
  return kind === "email" ? (
    <svg
      aria-hidden="true"
      className="contact-icon"
      viewBox="0 0 20 20"
      fill="none"
    >
      <path
        d="M3 5.5h14v9H3zM3.5 6l6.5 5 6.5-5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  ) : (
    <svg
      aria-hidden="true"
      className="contact-icon"
      viewBox="0 0 20 20"
      fill="none"
    >
      <path
        d="M6.1 3.5 8 6.8 6.8 8c.8 1.7 2.2 3.1 3.9 3.9l1.2-1.2 3.3 1.9-.5 2.1a1.5 1.5 0 0 1-1.7 1.1A12.6 12.6 0 0 1 4.2 7a1.5 1.5 0 0 1 1.1-1.7l.8-1.8Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}
