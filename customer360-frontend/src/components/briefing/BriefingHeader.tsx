import type { Account, Site } from "../../types/briefing";
import { ExportPDFButton } from "./ExportPDFButton";

interface BriefingHeaderProps {
  account: Account;
  site: Site;
}

export function BriefingHeader({ account, site }: BriefingHeaderProps) {
  const updatedAt = new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(site.last_updated));

  return (
    <header className="briefing-header">
      <nav aria-label="Breadcrumb" className="breadcrumb briefing-screen-only">
        <span>Customers</span>
        <span aria-hidden="true">/</span>
        <span>{account.name}</span>
        <span aria-hidden="true">/</span>
        <span aria-current="page">Customer Briefing</span>
      </nav>
      <div className="header-main">
        <div>
          <p className="page-kicker">ACCOUNT OVERVIEW</p>
          <h1>Customer Briefing</h1>
          <p className="header-account">
            {account.name}
            <span aria-hidden="true">·</span>
            {site.name}
          </p>
          <p className="updated-at">Last updated {updatedAt}</p>
        </div>
        <ExportPDFButton />
      </div>
    </header>
  );
}
