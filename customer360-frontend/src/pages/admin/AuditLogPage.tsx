import React from 'react';

/**
 * Audit Log Page (Admin Interface)
 * Corresponds to Audit Service in SDS Architecture and init.sql audit_logs table
 */
export const AuditLogPage: React.FC = () => {
    return (
        <div className="admin-page-container">
            <h2>Nhật ký hệ thống (Audit Logs)</h2>
            <p>Ghi nhận toàn bộ thao tác xác thực và truy cập theo SDS NFR.</p>
        </div>
    );
};

export default AuditLogPage;
