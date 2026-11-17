import type { CommercialFacts } from "../../types/briefing";
import { SectionHeading, StatusBadge } from "./BriefingPrimitives";

const currencyFormatter = (currency: string) =>
  new Intl.NumberFormat("en", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  });

export function CommercialFactsCard({
  commercial,
}: {
  commercial: CommercialFacts;
}) {
  const formatter = currencyFormatter(commercial.currency);
  const metrics = [
    {
      label: "Total sales revenue",
      value: formatter.format(commercial.total_sales_revenue),
      detail: commercial.currency,
    },
    {
      label: "Total quotation value",
      value: formatter.format(commercial.total_quotation_value),
      detail: `${commercial.quotation_count} quotations`,
    },
    {
      label: "Pending quotations",
      value: String(commercial.pending_quotations),
      detail: commercial.currency,
    },
    {
      label: "Approved quotations",
      value: String(commercial.approved_quotations),
      detail: commercial.currency,
    },
  ];

  return (
    <section aria-labelledby="commercial-title" className="card">
      <SectionHeading
        description={`Sales and quotation snapshot · ${commercial.currency}`}
        eyebrow="REVENUE"
        title="Commercial Facts"
        titleId="commercial-title"
      />
      <div className="metric-grid">
        {metrics.map((metric) => (
          <div className="metric-card" key={metric.label}>
            <p>{metric.label}</p>
            <strong>{metric.value}</strong>
            <span>{metric.detail}</span>
          </div>
        ))}
      </div>
      <div className="table-scroll">
        <table className="data-table commercial-table">
          <thead>
            <tr>
              <th scope="col">Record</th>
              <th scope="col">Description</th>
              <th scope="col">Date</th>
              <th scope="col">Amount</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {commercial.records.map((record) => (
              <tr key={record.id}>
                <td>
                  <strong>{record.reference}</strong>
                  <span className="table-subtext">{record.kind}</span>
                </td>
                <td>{record.description}</td>
                <td>
                  <time dateTime={record.date}>
                    {new Intl.DateTimeFormat("en", {
                      dateStyle: "medium",
                    }).format(new Date(`${record.date}T00:00:00`))}
                  </time>
                </td>
                <td className="amount-cell">
                  {currencyFormatter(record.currency).format(record.amount)}
                </td>
                <td>
                  <StatusBadge value={record.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
