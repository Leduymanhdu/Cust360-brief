/**
 * API Service for Customer 360
 * Communicates with Flask backend (http://127.0.0.1:5000) or falls back to static mock data
 * conforming to database/init.sql and the SDS Sequence Diagram.
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Static mock database for standalone frontend execution
const STATIC_FALLBACK_ACCOUNTS = [
    {
        id: "acc-001",
        legal_name: "Tập đoàn Công nghệ Viễn thông An Phát",
        tax_code: "0102345678",
        industry: "Công nghệ thông tin & Viễn thông",
        status: "ACTIVE",
        has_permission: true,
        sites: [
            { id: "site-101", site_name: "Trụ sở chính Cầu Giấy, Hà Nội", address: "Số 18 Phạm Hùng, Q. Cầu Giấy, Hà Nội" },
            { id: "site-102", site_name: "Chi nhánh miền Trung", address: "Số 45 Nguyễn Văn Linh, Q. Hải Châu, TP. Đà Nẵng" },
            { id: "site-103", site_name: "Trung tâm R&D TP.HCM", address: "Công viên phần mềm Quang Trung, Q. 12, TP.HCM" }
        ],
        briefing: {
            briefing_status: "COMPLETED",
            freshness_status: "Dữ liệu hợp đồng và tài chính đồng bộ trong 24 giờ qua.",
            validation_status: "VALID",
            sections: {
                company_overview: "Tập đoàn Công nghệ Viễn thông An Phát là đối tác hạ tầng mạng cấp 1. Doanh nghiệp có 3 địa điểm vận hành chính trên toàn quốc.",
                commercial_summary: "Tổng giá trị giao dịch: 45,200,000,000 VND qua 12 đơn hàng/hợp đồng. Tỷ lệ hoàn thành đúng hạn 98.5%.",
                risk_warnings: [
                    "Cảnh báo NFR: Không có hành vi tự động ghi ngược (No automatic write-back to CRM / ERP).",
                    "Hợp đồng PDF số 2026-HD-08 cần đối soát điều khoản bảo hành trước khi thanh toán."
                ]
            },
            citations: [
                {
                    citation_number: 1,
                    claim_text: "Doanh thu năm gần nhất đạt tăng trưởng 18.2%",
                    source_type: "COMMERCIAL",
                    validation_status: "VALID",
                    source_excerpt: "Bảng commercial_records (Hệ thống ERP)"
                },
                {
                    citation_number: 2,
                    claim_text: "Địa điểm nhà máy chính đáp ứng tiêu chuẩn an toàn công nghiệp",
                    source_type: "PDF",
                    validation_status: "VALID",
                    source_excerpt: "File Bien_ban_nghiem_thu_2026.pdf (Trang 4)"
                }
            ]
        }
    },
    {
        id: "acc-002",
        legal_name: "Công ty Cổ phần Sản xuất & Thương mại Đại Dương",
        tax_code: "0309876543",
        industry: "Sản xuất & Logistics công nghiệp",
        status: "ACTIVE",
        has_permission: true,
        sites: [
            { id: "site-201", site_name: "Nhà máy chính KCN Tân Bình", address: "Đường CN13, KCN Tân Bình, TP.HCM" },
            { id: "site-202", site_name: "Tổng kho logistics Bình Dương", address: "Đại lộ Bình Dương, TP. Thuận An, Bình Dương" }
        ],
        briefing: {
            briefing_status: "COMPLETED",
            freshness_status: "Cập nhật 2 ngày trước.",
            validation_status: "VALID",
            sections: {
                company_overview: "Đơn vị cung ứng bao bì và logistics hàng đầu miền Nam.",
                commercial_summary: "Doanh thu năm hiện tại: 32,800,000,000 VND.",
                risk_warnings: ["No automatic write-back to CRM / ERP."]
            },
            citations: [
                {
                    citation_number: 1,
                    claim_text: "Năng lực xuất kho đạt 15.000 tấn/tháng",
                    source_type: "COMMERCIAL",
                    validation_status: "VALID",
                    source_excerpt: "Báo cáo hoạt động Q3/2026"
                }
            ]
        }
    },
    {
        id: "acc-003",
        legal_name: "Tổng Công ty Dược phẩm Quốc tế Medico",
        tax_code: "0105558888",
        industry: "Y tế & Dược phẩm sinh học",
        status: "ACTIVE",
        has_permission: true,
        sites: [
            { id: "site-301", site_name: "Trụ sở Đống Đa", address: "Số 102 Tôn Thất Tùng, Đống Đa, Hà Nội" },
            { id: "site-302", site_name: "Chi nhánh Cần Thơ", address: "Số 20 Trần Phú, Ninh Kiều, Cần Thơ" }
        ],
        briefing: {
            briefing_status: "COMPLETED",
            freshness_status: "Cập nhật 5 giờ trước.",
            validation_status: "VALID",
            sections: {
                company_overview: "Nhà phân phối thiết bị y tế và dược phẩm đạt chuẩn GMP-WHO.",
                commercial_summary: "Giá trị hợp đồng khung: 18,500,000,000 VND.",
                risk_warnings: ["No automatic write-back to CRM / ERP."]
            },
            citations: [
                {
                    citation_number: 1,
                    claim_text: "Chứng chỉ GMP gia hạn đến tháng 12/2028",
                    source_type: "PDF",
                    validation_status: "VALID",
                    source_excerpt: "Giay_chung_nhan_GMP_2026.pdf"
                }
            ]
        }
    },
    {
        id: "acc-revoked-004",
        legal_name: "Công ty TNHH Năng lượng Tái tạo SunPower Việt Nam",
        tax_code: "0401122334",
        industry: "Năng lượng & Điện mặt trời",
        status: "INACTIVE",
        has_permission: false, // Permission revoked in diagram
        sites: [
            { id: "site-401", site_name: "Văn phòng Nha Trang", address: "Số 5 Pasteur, TP. Nha Trang, Khánh Hòa" }
        ],
        briefing: null
    },
    {
        id: "acc-005",
        legal_name: "Công ty Cổ phần Bán lẻ Tiêu dùng Toàn Cầu",
        tax_code: "0313456789",
        industry: "Bán lẻ & Chuỗi siêu thị",
        status: "ACTIVE",
        has_permission: true,
        sites: [
            { id: "site-501", site_name: "Văn phòng Quận 1", address: "Tòa nhà Bitexco, Q. 1, TP.HCM" }
        ],
        briefing: {
            briefing_status: "COMPLETED",
            freshness_status: "Cập nhật ngày hôm qua.",
            validation_status: "VALID",
            sections: {
                company_overview: "Chuỗi 60 siêu thị bán lẻ hiện đại với hơn 1.200 nhân viên.",
                commercial_summary: "Tổng giá trị mua sắm thiết bị: 14,300,000,000 VND.",
                risk_warnings: ["No automatic write-back to CRM / ERP."]
            },
            citations: []
        }
    }
];

export const ApiService = {
    /**
     * Authenticate user
     */
    async login(usernameOrEmail, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username_or_email: usernameOrEmail,
                    password: password
                })
            });
            const data = await response.json();
            if (!response.ok) {
                return { success: false, message: data.message || 'Đăng nhập không thành công.' };
            }
            return data;
        } catch (err) {
            console.warn('[API Service] Backend unreachable, using client-side mock login:', err);
            // Fallback for static demo
            return {
                success: true,
                message: "Đăng nhập thành công (Chế độ mô phỏng giao diện tĩnh).",
                user: {
                    id: "usr-demo",
                    email: usernameOrEmail,
                    full_name: usernameOrEmail.includes('@') ? usernameOrEmail.split('@')[0].toUpperCase() : usernameOrEmail,
                    role: "SALES",
                    is_active: true
                }
            };
        }
    },

    /**
     * Search accounts by keyword
     */
    async searchAccounts(query = '') {
        try {
            const url = `${API_BASE_URL}/accounts/search?query=${encodeURIComponent(query)}`;
            const response = await fetch(url);
            const data = await response.json();
            if (response.ok) {
                return data;
            }
            throw new Error(data.message || 'Lỗi tìm kiếm');
        } catch (err) {
            console.warn('[API Service] Backend unreachable, using client-side mock search:', err);
            // Fallback filter
            const q = query.trim().toLowerCase();
            const matched = q ? STATIC_FALLBACK_ACCOUNTS.filter(acc =>
                acc.legal_name.toLowerCase().includes(q) ||
                acc.tax_code.toLowerCase().includes(q) ||
                acc.industry.toLowerCase().includes(q)
            ) : STATIC_FALLBACK_ACCOUNTS;

            return {
                success: true,
                query: query,
                total: matched.length,
                data: matched,
                message: matched.length > 0 ? `Tìm thấy ${matched.length} tài khoản.` : "Không tìm thấy tài khoản phù hợp."
            };
        }
    },

    /**
     * Load Customer 360 Briefing (demonstrates Sequence Diagram permission check)
     */
    async getAccountBriefing(accountId) {
        try {
            const url = `${API_BASE_URL}/accounts/${accountId}/briefing`;
            const response = await fetch(url, {
                headers: { 'X-User-Id': 'usr-002' }
            });
            const data = await response.json();
            return {
                ok: response.ok,
                status: response.status,
                data: data
            };
        } catch (err) {
            console.warn('[API Service] Backend unreachable, simulating Sequence Diagram authorization flow:', err);
            const target = STATIC_FALLBACK_ACCOUNTS.find(a => a.id === accountId);
            if (!target) {
                return { ok: false, status: 404, data: { message: "Không tìm thấy tài khoản." } };
            }

            // Sequence diagram Alt branch: [Permission revoked] -> HTTP 403
            if (!target.has_permission) {
                return {
                    ok: false,
                    status: 403,
                    data: {
                        error: "HTTP 403 - Access Revoked",
                        message: "Quyền truy cập tài khoản đã bị thu hồi hoặc bạn không có quyền trong phạm vi tài khoản này (Account Scope).",
                        diagram_step: "Display access revoked",
                        account: target
                    }
                };
            }

            // Sequence diagram Alt branch: [Permission still valid] -> HTTP 200
            return {
                ok: true,
                status: 200,
                data: {
                    data: {
                        id: `brf-${target.id}`,
                        account_id: target.id,
                        legal_name: target.legal_name,
                        tax_code: target.tax_code,
                        industry: target.industry,
                        status: target.status,
                        briefing_status: "COMPLETED",
                        freshness_status: target.briefing?.freshness_status || "Đồng bộ gần nhất",
                        validation_status: "VALID",
                        sections: target.briefing?.sections || {},
                        citations: target.briefing?.citations || [],
                        system_notice: "Tuân thủ nghiêm ngặt: No automatic write-back to CRM / ERP"
                    }
                }
            };
        }
    }
};
