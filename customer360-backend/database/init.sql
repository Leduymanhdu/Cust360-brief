-- Bật extension để dùng UUID
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================
-- 1. BẢNG USERS (Người dùng hệ thống)
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL CHECK (role IN ('ADMIN', 'SALES', 'SERVICE')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. BẢNG ACCOUNTS & SITES (Khách hàng & Địa điểm)
-- =====================================================
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name VARCHAR(500) NOT NULL,
    tax_code VARCHAR(100) UNIQUE,
    industry VARCHAR(255),
    status VARCHAR(30) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    site_name VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT fk_sites_account FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE RESTRICT
);

-- =====================================================
-- 3. BẢNG USER_ACCOUNT_ACCESS (Phân quyền Account Scope)
-- =====================================================
CREATE TABLE user_account_access (
    user_id UUID NOT NULL,
    account_id UUID NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (user_id, account_id),
    CONSTRAINT fk_access_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_access_account FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE CASCADE
);

-- =====================================================
-- 4. BẢNG CROSSWALK (Ánh xạ ID nguồn)
-- =====================================================
CREATE TABLE crosswalk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system VARCHAR(100) NOT NULL,
    source_account_id VARCHAR(255) NOT NULL,
    source_account_name VARCHAR(500),
    account_id UUID NOT NULL,
    review_status VARCHAR(30) NOT NULL DEFAULT 'PENDING' 
        CHECK (review_status IN ('PENDING', 'APPROVED', 'REJECTED')),
    reviewed_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT fk_crosswalk_account FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE RESTRICT,
    CONSTRAINT fk_crosswalk_reviewer FOREIGN KEY (reviewed_by) 
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_crosswalk_source UNIQUE (source_system, source_account_id)
);

-- =====================================================
-- 5. BẢNG COMMERCIAL_RECORDS (Dữ liệu thương mại)
-- =====================================================
CREATE TABLE commercial_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    source_system VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(255) NOT NULL,
    record_type VARCHAR(30) NOT NULL CHECK (record_type IN ('QUOTATION', 'ORDER')),
    status VARCHAR(30) NOT NULL,
    currency CHAR(3) NOT NULL CHECK (currency IN ('VND', 'USD')),
    total_amount NUMERIC(20,2) NOT NULL DEFAULT 0,
    record_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT fk_commercial_account FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE RESTRICT,
    CONSTRAINT uq_commercial_source UNIQUE (source_system, source_record_id),
    CONSTRAINT ck_commercial_amount CHECK (total_amount >= 0)
);

-- =====================================================
-- 6. BẢNG PDF_TEXT (Bằng chứng từ PDF)
-- =====================================================
CREATE TABLE pdf_text (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_hash VARCHAR(128) NOT NULL,
    page_number INTEGER,
    extracted_text TEXT,
    injection_flag BOOLEAN NOT NULL DEFAULT FALSE,
    is_usable BOOLEAN NOT NULL DEFAULT TRUE,
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT fk_pdf_account FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE RESTRICT
);

-- =====================================================
-- 7. BẢNG BRIEFINGS (Bản tóm tắt AI)
-- =====================================================
CREATE TABLE briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    site_id UUID, -- Có thể null nếu xem toàn bộ công ty
    generated_by UUID NOT NULL,
    briefing_status VARCHAR(30) NOT NULL DEFAULT 'GENERATING' 
        CHECK (briefing_status IN ('GENERATING', 'COMPLETED', 'FAILED', 'BLOCKED')),
    sections JSONB NOT NULL DEFAULT '{}'::jsonb, -- Chứa nội dung 6 phần
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    validation_status VARCHAR(30) DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    CONSTRAINT fk_briefing_account FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE RESTRICT,
    CONSTRAINT fk_briefing_site FOREIGN KEY (site_id) 
        REFERENCES sites(id) ON DELETE SET NULL,
    CONSTRAINT fk_briefing_user FOREIGN KEY (generated_by) 
        REFERENCES users(id) ON DELETE RESTRICT
);

-- =====================================================
-- 8. BẢNG CITATIONS (Trích dẫn nguồn)
-- =====================================================
CREATE TABLE citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    briefing_id UUID NOT NULL,
    citation_number INTEGER NOT NULL,
    claim_text TEXT NOT NULL,
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('PDF', 'COMMERCIAL')),
    pdf_text_id UUID,
    commercial_record_id UUID,
    source_excerpt TEXT,
    validation_status VARCHAR(30) NOT NULL DEFAULT 'PENDING' 
        CHECK (validation_status IN ('PENDING', 'VALID', 'INVALID', 'REJECTED')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT fk_citation_briefing FOREIGN KEY (briefing_id) 
        REFERENCES briefings(id) ON DELETE CASCADE,
    CONSTRAINT fk_citation_pdf FOREIGN KEY (pdf_text_id) 
        REFERENCES pdf_text(id) ON DELETE RESTRICT,
    CONSTRAINT fk_citation_commercial FOREIGN KEY (commercial_record_id) 
        REFERENCES commercial_records(id) ON DELETE RESTRICT,
    CONSTRAINT uq_briefing_citation UNIQUE (briefing_id, citation_number),
    
    -- Ràng buộc: Nếu là PDF thì phải có pdf_text_id, nếu là COMMERCIAL thì phải có commercial_record_id
    CONSTRAINT ck_citation_source CHECK (
        (source_type = 'PDF' AND pdf_text_id IS NOT NULL AND commercial_record_id IS NULL)
        OR
        (source_type = 'COMMERCIAL' AND commercial_record_id IS NOT NULL AND pdf_text_id IS NULL)
    )
);

-- =====================================================
-- 9. BẢNG AUDIT_LOGS (Nhật ký hệ thống)
-- =====================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- TẠO INDEX ĐỂ TĂNG TỐC TRUY VẤN (Theo yêu cầu NFR)
-- =====================================================
CREATE INDEX idx_accounts_legal_name ON accounts USING gin(to_tsvector('simple', legal_name));
CREATE INDEX idx_commercial_account_date ON commercial_records(account_id, record_date);
CREATE INDEX idx_pdf_account ON pdf_text(account_id);
CREATE INDEX idx_pdf_hash ON pdf_text(file_hash);
CREATE INDEX idx_briefings_account_date ON briefings(account_id, created_at DESC);
CREATE INDEX idx_citations_briefing ON citations(briefing_id);
CREATE INDEX idx_audit_user_date ON audit_logs(user_id, created_at DESC);