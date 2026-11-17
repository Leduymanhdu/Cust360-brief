import { AccountSiteCard } from "../components/briefing/AccountSiteCard";
import { BriefingHeader } from "../components/briefing/BriefingHeader";
import { CommercialFactsCard } from "../components/briefing/CommercialFactsCard";
import { ContactsRolesCard } from "../components/briefing/ContactsRolesCard";
import { RecentInteractionsCard } from "../components/briefing/RecentInteractionsCard";
import { ServiceIssuesCard } from "../components/briefing/ServiceIssuesCard";
import { SuggestedQuestionsCard } from "../components/briefing/SuggestedQuestionsCard";
import { briefingMock } from "../data/briefing.mock";
import "../styles/briefing.css";

export default function BriefingPage() {
  const { account, site, contacts, interactions, commercial, service_issues } =
    briefingMock.content;

  return (
    <main className="briefing-page">
      <BriefingHeader account={account} site={site} />
      <div className="briefing-content">
        <AccountSiteCard account={account} site={site} />
        <ContactsRolesCard contacts={contacts} />
        <RecentInteractionsCard interactions={interactions} />
        <CommercialFactsCard commercial={commercial} />
        <ServiceIssuesCard issues={service_issues} />
        <SuggestedQuestionsCard
          questions={briefingMock.content.suggested_questions}
          gaps={briefingMock.content.information_gaps}
        />
      </div>
      <footer className="briefing-footer briefing-screen-only">
        <span>Briefing reference {briefingMock.briefing_id}</span>
        <span>Demonstration data · Not connected to live customer records</span>
      </footer>
    </main>
  );
}
