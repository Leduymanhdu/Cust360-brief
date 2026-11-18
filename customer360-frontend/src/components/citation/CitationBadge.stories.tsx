import type { Meta, StoryObj } from '@storybook/react';
import { CitationBadge } from './CitationBadge';
import type { Citation } from '../../types/briefing';

const meta: Meta<typeof CitationBadge> = {
  title: 'Briefing/CitationBadge',
  component: CitationBadge,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Badge [n] hiển thị cạnh câu khẳng định trong Briefing. ' +
          'Hover hoặc click để xem chi tiết trích dẫn.',
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof CitationBadge>;

const pdfCitation: Citation = {
  id: 'cit-001',
  briefing_id: 'brief-abc',
  citation_number: 1,
  claim_text: 'Doanh thu Q3/2024 đạt 15.2 tỷ VND, tăng 23% so với cùng kỳ năm ngoái.',
  source_type: 'PDF',
  source_name: 'BaoCaoTaiChinh_Q3_2024.pdf',
  page_number: 12,
  source_excerpt:
    'Tổng doanh thu trong quý III năm 2024 đạt 15,215 tỷ đồng, tương đương mức tăng trưởng 23.1% so với Q3/2023.',
  validation_status: 'VALID',
};

const commercialCitation: Citation = {
  id: 'cit-002',
  briefing_id: 'brief-abc',
  citation_number: 2,
  claim_text: 'Khách hàng có 3 đơn hàng đang xử lý với tổng giá trị 850 triệu VND.',
  source_type: 'COMMERCIAL',
  source_name: 'SAP ERP',
  page_number: undefined,
  source_excerpt: undefined,
  validation_status: 'PENDING',
};

const invalidCitation: Citation = {
  id: 'cit-003',
  briefing_id: 'brief-abc',
  citation_number: 3,
  claim_text: 'Số lượng nhân viên công ty là 1,200 người.',
  source_type: 'PDF',
  source_name: 'HoSoCongTy_2023.pdf',
  page_number: 5,
  validation_status: 'INVALID',
};

export const PDFWithPageNumber: Story = {
  args: {
    citationNumber: 1,
    citation: pdfCitation,
  },
};

export const CommercialSource: Story = {
  args: {
    citationNumber: 2,
    citation: commercialCitation,
  },
};

export const InvalidCitation: Story = {
  args: {
    citationNumber: 3,
    citation: invalidCitation,
  },
};

export const Loading: Story = {
  args: {
    citationNumber: 1,
    citation: undefined,
    isLoading: true,
  },
};

export const NotFound: Story = {
  args: {
    citationNumber: 99,
    citation: undefined,
    isLoading: false,
  },
};

export const InlineWithText: Story = {
  render: () => (
    <p style={{ maxWidth: 500, lineHeight: 1.7, fontFamily: 'sans-serif', fontSize: 14 }}>
      Doanh thu Q3/2024 đạt 15.2 tỷ VND, tăng 23% so với cùng kỳ năm ngoái
      <CitationBadge citationNumber={1} citation={pdfCitation} />. Khách hàng
      hiện có 3 đơn hàng đang xử lý với tổng giá trị 850 triệu VND
      <CitationBadge citationNumber={2} citation={commercialCitation} />.
    </p>
  ),
};
