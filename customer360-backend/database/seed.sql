-- =====================================================
-- CUSTOMER 360 - DATA SEED V4 (Fix Schema & Data Consistency)
-- =====================================================

-- 1. USERS (Sử dụng Bcrypt hash chuẩn cho mật khẩu: "password123")
-- Hash này được tạo bởi bcrypt: $2a$12$IbUZbCEBvkmo/KxSp65LXe2Rgj7ARcOFMs0D/quCu2JMRqXVnp7Iu
INSERT INTO users (id, email, password_hash, full_name, role, is_active) VALUES
('11111111-1111-1111-1111-111111111111', 'admin@cust360.vn', '$2a$12$IbUZbCEBvkmo/KxSp65LXe2Rgj7ARcOFMs0D/quCu2JMRqXVnp7Iu', 'Nguyễn Quản Trị', 'ADMIN', TRUE),
('22222222-2222-2222-2222-222222222222', 'sales@cust360.vn', '$2a$12$IbUZbCEBvkmo/KxSp65LXe2Rgj7ARcOFMs0D/quCu2JMRqXVnp7Iu', 'Trần Thị Thu Thảo', 'SALES', TRUE),
('33333333-3333-3333-3333-333333333333', 'service@cust360.vn', '$2a$12$IbUZbCEBvkmo/KxSp65LXe2Rgj7ARcOFMs0D/quCu2JMRqXVnp7Iu', 'Lê Hoàng Nam', 'SERVICE', TRUE);

-- 2. ACCOUNTS
INSERT INTO accounts (id, legal_name, tax_code, industry, status) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'Tập đoàn Công nghệ Viễn thông An Phát', '0102345678', 'Công nghệ thông tin & Viễn thông', 'ACTIVE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'Công ty Cổ phần Sản xuất & Thương mại Đại Dương', '0309876543', 'Sản xuất & Logistics công nghiệp', 'ACTIVE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'Tổng Công ty Dược phẩm Quốc tế Medico', '0105558888', 'Y tế & Dược phẩm sinh học', 'ACTIVE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 'Công ty TNHH Năng lượng Tái tạo SunPower Việt Nam', '0401122334', 'Năng lượng & Điện mặt trời', 'INACTIVE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'Công ty Cổ phần Bán lẻ Tiêu dùng Toàn Cầu', '0313456789', 'Bán lẻ & Chuỗi siêu thị', 'ACTIVE');

-- 3. SITES
INSERT INTO sites (id, account_id, site_name, address) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'Trụ sở chính Cầu Giấy, Hà Nội', 'Số 18 Phạm Hùng, Q. Cầu Giấy, Hà Nội'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'Chi nhánh miền Trung', 'Số 45 Nguyễn Văn Linh, Q. Hải Châu, TP. Đà Nẵng'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'Nhà máy chính KCN Tân Bình', 'Đường CN13, KCN Tân Bình, TP.HCM');

-- 4. USER_ACCOUNT_ACCESS (Sales không có quyền xem SunPower acc-004)
INSERT INTO user_account_access (user_id, account_id) VALUES
('22222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'),
('22222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'),
('22222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'),
('22222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5');

-- 5. COMMERCIAL_RECORDS (Khớp chính xác số liệu: 2 đơn hàng, tổng 45.2 tỷ)
INSERT INTO commercial_records (id, account_id, source_system, source_record_id, record_type, status, currency, total_amount, record_date) VALUES
('cccccccc-cccc-cccc-cccc-ccccccccccc1', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'ERP', 'HD-2025-001', 'ORDER', 'COMPLETED', 'VND', 15000000000.00, CURRENT_DATE - 30),
('cccccccc-cccc-cccc-cccc-ccccccccccc2', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'ERP', 'HD-2026-008', 'ORDER', 'COMPLETED', 'VND', 30200000000.00, CURRENT_DATE - 5);

-- 6. PDF_TEXT
INSERT INTO pdf_text (id, account_id, file_name, file_hash, page_number, extracted_text, injection_flag, is_usable, extracted_at) VALUES
('dddddddd-dddd-dddd-dddd-ddddddddd001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'Bien_ban_nghiem_thu_2026.pdf', 'hash_001', 4, 'Địa điểm nhà máy chính đáp ứng tiêu chuẩn an toàn công nghiệp. Đã ký nghiệm thu.', FALSE, TRUE, NOW());

-- 7. BRIEFINGS (Cấu trúc JSONB đúng 6 phần, mỗi phần có content & citations)
INSERT INTO briefings (id, account_id, site_id, generated_by, briefing_status, sections, is_stale, validation_status, created_at) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', '22222222-2222-2222-2222-222222222222', 'COMPLETED', 
'{
  "account_and_site": {
    "content": "Tập đoàn Công nghệ Viễn thông An Phát (MST: 0102345678). Địa điểm đang chọn: Trụ sở chính Cầu Giấy, Hà Nội.",
    "citations": []
  },
  "contacts_and_roles": {
    "content": "Không có thông tin liên hệ nào trong phạm vi dữ liệu được cung cấp.",
    "citations": []
  },
  "recent_interactions": {
    "content": "Tài liệu nghiệm thu ghi nhận nhà máy chính đáp ứng tiêu chuẩn an toàn công nghiệp.",
    "citations": [3]
  },
  "commercial_facts": {
    "content": "Tổng giá trị giao dịch ghi nhận: 45,200,000,000 VND qua 2 đơn hàng/hợp đồng (HD-2025-001 và HD-2026-008).",
    "citations": [1, 2]
  },
  "service_issues": {
    "content": "Không có sự cố dịch vụ nào đang mở trong phạm vi dữ liệu.",
    "citations": []
  },
  "suggested_questions_and_gaps": {
    "content": "Gợi ý: Xác nhận kế hoạch tiếp theo cho đơn hàng HD-2026-008. Khoảng trống: Thiếu dữ liệu liên hệ của người đại diện.",
    "citations": []
  }
}', FALSE, 'PASSED', NOW() - INTERVAL '1 day');

-- 8. CITATIONS (Mỗi trích dẫn gắn với một bản ghi nguồn)
INSERT INTO citations (briefing_id, citation_number, claim_text, source_type, commercial_record_id, source_excerpt, validation_status) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1', 1, 'Đơn hàng HD-2025-001 hoàn tất với giá trị 15,000,000,000 VND.', 'COMMERCIAL', 'cccccccc-cccc-cccc-cccc-ccccccccccc1', 'HD-2025-001 | ORDER | COMPLETED | VND 15,000,000,000.00', 'VALID'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1', 2, 'Đơn hàng HD-2026-008 hoàn tất với giá trị 30,200,000,000 VND.', 'COMMERCIAL', 'cccccccc-cccc-cccc-cccc-ccccccccccc2', 'HD-2026-008 | ORDER | COMPLETED | VND 30,200,000,000.00', 'VALID');

INSERT INTO citations (briefing_id, citation_number, claim_text, source_type, pdf_text_id, source_excerpt, validation_status) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1', 3, 'Nhà máy chính đáp ứng tiêu chuẩn an toàn công nghiệp.', 'PDF', 'dddddddd-dddd-dddd-dddd-ddddddddd001', 'Địa điểm nhà máy chính đáp ứng tiêu chuẩn an toàn công nghiệp. Đã ký nghiệm thu.', 'VALID');