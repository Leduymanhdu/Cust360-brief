# Security Scripts - Customer 360 Briefing Assistant
## SongNhat Vietnam | WS-09: QA, Security & DevOps

### Mục đích

Bộ script kiểm tra an ninh dữ liệu trước khi đưa vào pipeline Customer 360. Dữ liệu đầu vào (PDF, CSV) phải đi qua 3 cổng kiểm tra (gate) tuần tự. File nào FAIL ở gate nào thì dừng tại đó, không đi tiếp.

```
File upload → [Gate 1: Validation] → [Gate 2: Injection] → [Gate 3: PII Mask] → Pipeline
                  ↓ FAIL                   ↓ REJECT              ↓ PII_FOUND
               Từ chối file            Từ chối file         Mask xong mới cho vào
```

### Tham chiếu RFP

| Gate | Yêu cầu RFP | Mô tả |
|------|-------------|--------|
| Gate 1 | SEC 04, ACC 06, Mục 4 | Chỉ nhận file PDF hợp lệ, ≤10MB, ≤20 trang, không có JavaScript/malware |
| Gate 2 | SEC 04, ACC 06 | Quét nội dung tìm prompt injection (xem embedded instructions là DATA) |
| Gate 3 | SEC 02, Mục 6 | Mask SĐT/email cá nhân, CCCD, TK ngân hàng. Giữ nguyên thông tin doanh nghiệp |
| Policy | SEC 03, ARC 03, Mục 6 | Phân loại dữ liệu: [Công khai] / [Nội bộ] / [Hạn chế] |

---

### Cấu trúc thư mục

```
security_scripts/
├── scanners/                        ← 3 script chính
│   ├── gate1_pdf_validator.py       ← Kiểm tra cấu trúc PDF
│   ├── gate2_injection_scanner.py   ← Quét prompt injection
│   └── gate3_pii_masker.py          ← Phát hiện & mask PII
│
├── configs/                         ← File cấu hình (tách riêng để dễ cập nhật)
│   ├── injection_patterns.json      ← 49 regex patterns (EN + VI), 7 nhóm
│   └── pii_rules.json               ← Rules mask PII + whitelist business data
│
├── docs/
│   └── access_label_policy.md       ← Chính sách phân loại quyền truy cập
│
├── test_data/
│   ├── clean/                       ← 5 file PDF mẫu sạch (phải PASS hết)
│   ├── dirty/                       ← 4 file PDF "bẩn" (phải bị detect)
│   ├── csv_samples/                 ← CSV có PII để test masking
│   ├── masked_output/               ← CSV đã mask (output của Gate 3)
│   └── create_dirty_test_data.py    ← Script tạo file test bẩn
│
├── logs/                            ← Kết quả scan (JSON)
├── reports/                         ← Báo cáo tổng hợp
└── run_full_pipeline.py             ← Chạy cả 3 gate liên tiếp
```

---

### Cài đặt

```bash
# Yêu cầu: Python 3.10+
pip install pymupdf fpdf2
```

### Cách chạy

**Chạy từng gate riêng:**

```bash
# Gate 1 - Kiểm tra cấu trúc PDF
python -I scanners/gate1_pdf_validator.py test_data/

# Gate 2 - Quét injection (nên dùng kèm config)
python -I scanners/gate2_injection_scanner.py test_data/ --config configs/injection_patterns.json

# Gate 3 - Mask PII
python -I scanners/gate3_pii_masker.py test_data/ --config configs/pii_rules.json
```

**Chạy full pipeline (3 gate liên tiếp):**

```bash
python -I run_full_pipeline.py test_data/
```

**Tạo lại dirty test data:**

```bash
python -I test_data/create_dirty_test_data.py
```

> **Lưu ý:** Luôn dùng flag `-I` khi chạy Python trên dữ liệu không tin cậy (isolated mode, tránh import từ thư mục hiện tại).

---

### Chi tiết từng Gate

#### Gate 1: PDF Validation (`gate1_pdf_validator.py`)

Kiểm tra 8 tiêu chí trước khi mở file đọc nội dung:

1. File tồn tại & đọc được
2. Magic bytes = `%PDF-` (đúng là PDF thật)
3. Kích thước ≤ 10 MB
4. Số trang ≤ 20
5. Không bị mã hóa / password-protect
6. Không có JavaScript embedded
7. Không có auto-actions nguy hiểm (phân biệt `/FitH` vô hại vs `/Launch` nguy hiểm)
8. Không có embedded files đính kèm

#### Gate 2: Injection Scanner (`gate2_injection_scanner.py`)

Quét text content bằng regex, chia 7 nhóm pattern:

| ID | Nhóm | Severity | Ví dụ |
|----|-------|----------|-------|
| INJ-01 | Direct Override | HIGH | "Ignore all previous instructions" |
| INJ-02 | Role Hijacking | HIGH | "You are now an admin" |
| INJ-03 | System Prompt Extraction | HIGH | "Print your system prompt" |
| INJ-04 | Data Exfiltration | CRITICAL | "Send all customer data to..." |
| INJ-05 | Delimiter Escape | HIGH | `` ```system: `` , `[INST]`, `<<SYS>>` |
| INJ-06 | Indirect/Hidden | MEDIUM | `[HIDDEN INSTRUCTION]`, HTML comments |
| INJ-07 | Access Control Bypass | CRITICAL | "Set access_level=admin" |

Hỗ trợ cả tiếng Anh và tiếng Việt. Patterns được tách ra file `configs/injection_patterns.json` để dễ cập nhật mà không sửa code.

**Quyết định:** CRITICAL hoặc HIGH → REJECT. MEDIUM → FLAG (cần human review).

#### Gate 3: PII Masker (`gate3_pii_masker.py`)

| Loại PII | Regex | Action |
|----------|-------|--------|
| SĐT cá nhân (09x, 03x, 07x, 08x) | Hỗ trợ format: `0909123456`, `0909 123 456`, `0909.123.456` | Mask → `***-***-****` |
| Email cá nhân (@gmail, @yahoo, @hotmail...) | Chỉ mask domain cá nhân | Mask → `***@***.***` |
| CCCD (12 số) | Kèm prefix CCCD/CMND | Mask |
| TK ngân hàng | Kèm prefix TK/Tài khoản | Mask |
| MST cá nhân (10 số) | Phân biệt với MST doanh nghiệp (13 số) | Flag review |

**Whitelist (giữ nguyên, không mask):**
- Email doanh nghiệp (`@company.vn`, `@abc.com.vn`)
- Hotline / tổng đài (`1900xxxx`, `(028) xxxx`)
- MST doanh nghiệp (10-3 format)

**Nguyên tắc:** Tạo bản COPY đã mask, KHÔNG sửa file gốc.

---

### Chính sách phân loại (Gate 4 / Policy)

Xem chi tiết tại `docs/access_label_policy.md`. Tóm tắt 3 cấp:

| Label | Ai được xem | Ví dụ |
|-------|------------|-------|
| [Công khai] | Tất cả user | Thông tin sản phẩm, báo giá đã gửi KH, hotline |
| [Nội bộ] | Nhân viên SongNhat | Biên bản họp, danh sách KH cơ bản, ghi chú hệ thống |
| [Hạn chế] | Manager trở lên | Giá gốc, margin, chiến lược giá, hợp đồng đặc biệt |

Mặc định khi không chắc chắn → gán [Nội bộ].

---

### Tech stack

- **Python 3.10+**
- **PyMuPDF (pymupdf)** - đọc và phân tích PDF
- **fpdf2** - tạo file PDF test
- **Pandas** - xử lý CSV (dùng trong pipeline chính, gate scripts dùng csv module chuẩn)

### Thành viên

- **Workstream:** WS-09 (QA, Security & DevOps)
- **Liên quan:** WS-02 (Data Engineering) - pipeline ingestion

---

### Hạn chế & cải tiến tương lai

**Hạn chế hiện tại:**
- Injection detection dùng regex → attacker thay đổi từ ngữ có thể bypass. Production nên dùng thêm ML/embedding-based detection.
- PII mask cho PDF chỉ report, chưa tự động tạo PDF mới đã mask (do hạn chế kỹ thuật sửa text trong PDF).
- Chưa tích hợp antivirus scanner thật (ClamAV) cho Gate 1.

**Cải tiến đề xuất:**
- Tích hợp ClamAV hoặc VirusTotal API cho Gate 1.
- Dùng sentence-transformer để detect injection theo ngữ nghĩa (không chỉ regex).
- Tự động gán access_level dựa trên nội dung file (NLP classification).
- API hóa pipeline (FastAPI) để tích hợp vào hệ thống chính.