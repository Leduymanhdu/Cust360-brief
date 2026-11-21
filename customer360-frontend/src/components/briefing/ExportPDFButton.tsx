export function ExportPDFButton() {
  return (
    <button
      className="button button-primary briefing-screen-only"
      onClick={() => window.print()}
      type="button"
    >
      <svg aria-hidden="true" viewBox="0 0 20 20" fill="none">
        <path
          d="M6 7V3.5h8V7m-8 7H4.5A1.5 1.5 0 0 1 3 12.5v-3A1.5 1.5 0 0 1 4.5 8h11A1.5 1.5 0 0 1 17 9.5v3a1.5 1.5 0 0 1-1.5 1.5H14m-8-2h8v5H6z"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <circle cx="14.3" cy="10.6" r=".8" fill="currentColor" />
      </svg>
      Export PDF
    </button>
  );
}
