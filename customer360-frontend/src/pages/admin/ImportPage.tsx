import React from 'react';

/**
 * Data Import Page (Admin Interface)
 * Matches SDS M7-M8 data staging for Commercial & PDF records
 */
export const ImportPage: React.FC = () => {
    return (
        <div className="admin-page-container">
            <h2>Nhập dữ liệu nguồn (Data Ingestion)</h2>
            <p>Hỗ trợ nhập hợp đồng PDF và bảng kê thương mại từ CRM/ERP.</p>
        </div>
    );
};

export default ImportPage;
