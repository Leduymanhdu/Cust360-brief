import type { Account, Site } from "../../types/briefing";
import { SectionHeading, StatusBadge } from "./BriefingPrimitives";

interface AccountSiteCardProps {
  account: Account;
  site: Site;
}

export function AccountSiteCard({ account, site }: AccountSiteCardProps) {
  return (
    <section aria-labelledby="account-site-title" className="card">
      <SectionHeading
        description="Account profile and primary operating location."
        eyebrow="CUSTOMER PROFILE"
        title="Account & Site"
        titleId="account-site-title"
      />
      <div className="account-site-grid">
        <div className="profile-block">
          <div className="subsection-title">
            <h3>Account information</h3>
            <StatusBadge value={account.status} />
          </div>
          <dl className="detail-grid">
            <div className="detail-item detail-item-wide">
              <dt>Account name</dt>
              <dd>{account.name}</dd>
            </div>
            <div className="detail-item">
              <dt>Account ID</dt>
              <dd>{account.id}</dd>
            </div>
            <div className="detail-item">
              <dt>Account type</dt>
              <dd>{account.type}</dd>
            </div>
            <div className="detail-item">
              <dt>Industry</dt>
              <dd>{account.industry}</dd>
            </div>
            <div className="detail-item">
              <dt>Account owner</dt>
              <dd>{account.owner}</dd>
            </div>
          </dl>
        </div>
        <div className="profile-block site-block">
          <div className="subsection-title">
            <h3>Primary site</h3>
          </div>
          <dl className="detail-grid">
            <div className="detail-item detail-item-wide">
              <dt>Site name</dt>
              <dd>{site.name}</dd>
            </div>
            <div className="detail-item detail-item-wide">
              <dt>Address</dt>
              <dd>{site.address}</dd>
            </div>
            <div className="detail-item">
              <dt>Location</dt>
              <dd>{site.location}</dd>
            </div>
            <div className="detail-item">
              <dt>Last updated</dt>
              <dd>
                <time dateTime={site.last_updated}>
                  {new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(
                    new Date(site.last_updated),
                  )}
                </time>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </section>
  );
}
