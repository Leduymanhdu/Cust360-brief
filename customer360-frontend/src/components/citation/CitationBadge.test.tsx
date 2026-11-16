// ============================================================
// CitationBadge.test.tsx
// KAN-20 – Unit tests cho CitationBadge component
// Stack: Vitest + React Testing Library
// ============================================================

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CitationBadge } from './CitationBadge';
import type { Citation } from '../../types/briefing';

// ── Mock data ────────────────────────────────────────────────

const mockPdfCitation: Citation = {
  id: 'cit-001',
  briefing_id: 'brief-abc',
  citation_number: 1,
  claim_text: 'Doanh thu Q3 đạt 15.2 tỷ VND',
  source_type: 'PDF',
  source_name: 'BaoCao_Q3.pdf',
  page_number: 12,
  source_excerpt: 'Tổng doanh thu trong quý III...',
  validation_status: 'VALID',
};

const mockCommercialCitation: Citation = {
  id: 'cit-002',
  briefing_id: 'brief-abc',
  citation_number: 2,
  claim_text: 'Có 3 đơn hàng đang xử lý',
  source_type: 'COMMERCIAL',
  source_name: 'SAP ERP',
  validation_status: 'PENDING',
};

// ── Tests ─────────────────────────────────────────────────────

describe('CitationBadge', () => {
  describe('Rendering', () => {
    it('renders badge with citation number', () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      expect(screen.getByRole('button', { name: /trích dẫn số 1/i })).toBeDefined();
      expect(screen.getByText('[1]')).toBeDefined();
    });

    it('renders skeleton when isLoading=true', () => {
      render(<CitationBadge citationNumber={1} isLoading={true} />);
      expect(screen.getByText('[·]')).toBeDefined();
      expect(screen.queryByRole('button')).toBeNull();
    });

    it('renders unknown badge when citation is undefined and not loading', () => {
      render(<CitationBadge citationNumber={99} citation={undefined} isLoading={false} />);
      expect(screen.getByText('[99]')).toBeDefined();
    });
  });

  describe('Tooltip – Hover', () => {
    it('shows tooltip on mouse enter', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      const badge = screen.getByRole('button');

      fireEvent.mouseEnter(badge);

      await waitFor(() => {
        expect(screen.getByRole('tooltip')).toBeDefined();
        expect(screen.getByText('Doanh thu Q3 đạt 15.2 tỷ VND')).toBeDefined();
      });
    });

    it('hides tooltip on mouse leave', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      const badge = screen.getByRole('button');

      fireEvent.mouseEnter(badge);
      await waitFor(() => expect(screen.getByRole('tooltip')).toBeDefined());

      fireEvent.mouseLeave(badge);
      await waitFor(() => expect(screen.queryByRole('tooltip')).toBeNull());
    });

    it('shows PDF source type and page number', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      fireEvent.mouseEnter(screen.getByRole('button'));

      await waitFor(() => {
        expect(screen.getByText(/PDF/i)).toBeDefined();
        expect(screen.getByText(/Trang 12/i)).toBeDefined();
      });
    });

    it('shows COMMERCIAL source type without page number', async () => {
      render(<CitationBadge citationNumber={2} citation={mockCommercialCitation} />);
      fireEvent.mouseEnter(screen.getByRole('button'));

      await waitFor(() => {
        expect(screen.getByText(/CSV \/ Thương mại/i)).toBeDefined();
        expect(screen.queryByText(/Trang/i)).toBeNull();
      });
    });

    it('shows source excerpt when available', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      fireEvent.mouseEnter(screen.getByRole('button'));

      await waitFor(() => {
        expect(screen.getByText(/Tổng doanh thu trong quý III/i)).toBeDefined();
      });
    });

    it('shows validation badge when status is VALID', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      fireEvent.mouseEnter(screen.getByRole('button'));

      await waitFor(() => {
        expect(screen.getByText(/Đã xác minh/i)).toBeDefined();
      });
    });
  });

  describe('Tooltip – Pin (click)', () => {
    it('pins tooltip on click', async () => {
      const user = userEvent.setup();
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      const badge = screen.getByRole('button');

      await user.click(badge);
      expect(screen.getByRole('tooltip')).toBeDefined();

      // Move mouse away – tooltip should still be visible (pinned)
      fireEvent.mouseLeave(badge);
      await waitFor(() => {
        expect(screen.getByRole('tooltip')).toBeDefined();
      });
    });

    it('closes pinned tooltip on Escape key', async () => {
      const user = userEvent.setup();
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);

      await user.click(screen.getByRole('button'));
      expect(screen.getByRole('tooltip')).toBeDefined();

      await user.keyboard('{Escape}');
      await waitFor(() => expect(screen.queryByRole('tooltip')).toBeNull());
    });
  });

  describe('Accessibility', () => {
    it('has aria-label on badge button', () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      const btn = screen.getByRole('button');
      expect(btn.getAttribute('aria-label')).toMatch(/trích dẫn số 1/i);
    });

    it('sets aria-expanded=true when tooltip visible', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      const badge = screen.getByRole('button');

      fireEvent.mouseEnter(badge);
      await waitFor(() => {
        expect(badge.getAttribute('aria-expanded')).toBe('true');
      });
    });

    it('tooltip has role=tooltip', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      fireEvent.mouseEnter(screen.getByRole('button'));
      await waitFor(() => {
        expect(screen.getByRole('tooltip')).toBeDefined();
      });
    });

    it('shows tooltip on focus', async () => {
      render(<CitationBadge citationNumber={1} citation={mockPdfCitation} />);
      fireEvent.focus(screen.getByRole('button'));
      await waitFor(() => expect(screen.getByRole('tooltip')).toBeDefined());
    });
  });
});
