import type { Contact } from "../../types/briefing";
import { ContactIcon, SectionHeading } from "./BriefingPrimitives";

export function ContactsRolesCard({ contacts }: { contacts: Contact[] }) {
  return (
    <section aria-labelledby="contacts-title" className="card">
      <SectionHeading
        description="Key people associated with this account."
        eyebrow="PEOPLE"
        title="Contacts & Roles"
        titleId="contacts-title"
        trailing={<span className="count-pill">{contacts.length} contacts</span>}
      />
      <div className="contact-list">
        {contacts.map((contact) => (
          <article className="contact-row" key={contact.id}>
            <div className="contact-avatar" aria-hidden="true">
              {contact.full_name
                .split(" ")
                .map((part) => part[0])
                .slice(-2)
                .join("")}
            </div>
            <div className="contact-details">
              <div className="contact-name-line">
                <h3>{contact.full_name}</h3>
                {contact.is_primary ? (
                  <span className="primary-label">Primary contact</span>
                ) : null}
              </div>
              <p className="contact-title">
                {contact.job_title} <span>·</span> {contact.department}
              </p>
              <div className="contact-links">
                <a href={`mailto:${contact.email}`}>
                  <ContactIcon kind="email" />
                  {contact.email}
                </a>
                <a href={`tel:${contact.phone.replace(/[^\d+]/g, "")}`}>
                  <ContactIcon kind="phone" />
                  {contact.phone}
                </a>
              </div>
              <p className="contact-role">{contact.role}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
