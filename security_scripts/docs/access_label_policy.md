# CHÍNH SÁCH PHÂN LOẠI QUYỀN TRUY CẬP DỮ LIỆU
## Customer 360 Briefing Assistant - SongNhat Vietnam

**Phiên bản:** 1.0  
**Ngày ban hành:** 15/11/2026  
**Tham chiếu RFP:** SEC 03 (Business Secrecy), ARC 03 (Pre-retrieval Permission Filtering), Mục 6 (Tiêu chí đánh giá)

---

## 1. MỤC ĐÍCH

Tài liệu này định nghĩa **3 cấp độ truy cập** (access labels) cho tất cả dữ liệu đi vào pipeline Customer 360. Mỗi file và mỗi dòng dữ liệu (data row) phải được gán label TRƯỚC KHI đưa vào hệ thống retrieval.

**Mục tiêu:**
- Đảm bảo AI Briefing Assistant chỉ trả về thông tin phù hợp với quyền người dùng (ARC 03)
- Bảo vệ bí mật kinh doanh (SEC 03)
- Tuân thủ tiêu chí đánh giá chuẩn hóa dữ liệu (Mục 6)

---

## 2. ĐỊNH NGHĨA 3 CẤP ĐỘ TRUY CẬP

### 2.1. [Công khai] - Public
**Định nghĩa:** Thông tin có thể chia sẻ rộng rãi, không gây rủi ro nếu bên ngoài đọc được.

**Ví dụ:**
- Thông tin sản phẩm đã công bố (tên, mô tả, SKU công khai)
- Báo giá đã gửi khách hàng (quotation đã duyệt)
- Thông tin liên hệ công ty (hotline, email chung, địa chỉ văn phòng)
- Biên bản họp không chứa thông tin nhạy cảm

**Ai được truy cập:** Tất cả user trong hệ thống.

### 2.2. [Nội bộ] - Internal
**Định nghĩa:** Thông tin chỉ dành cho nhân viên SongNhat. Không gây thiệt hại nghiêm trọng nếu lộ, nhưng không nên chia sẻ ra ngoài.

**Ví dụ:**
- Biên bản họp nội bộ có thảo luận chiến lược
- Ghi chú hệ thống (Notes) về quy trình xử lý
- Thông tin khách hàng cơ bản (tên công ty, ngành, khu vực)
- Lịch sử đơn hàng tổng hợp (không có giá gốc/margin)
- Danh sách liên hệ nội bộ

**Ai được truy cập:** Nhân viên SongNhat có tài khoản hệ thống.

### 2.3. [Hạn chế] - Restricted
**Định nghĩa:** Thông tin nhạy cảm, gây thiệt hại kinh doanh hoặc pháp lý nếu lộ. Cần kiểm soát chặt chẽ.

**Ví dụ:**
- Giá gốc (cost price), tỷ suất lợi nhuận (margin)
- Chiến lược giá, chính sách chiết khấu đặc biệt theo khách hàng
- Thông tin tài chính nội bộ (doanh thu theo kênh, nợ xấu)
- Dữ liệu cá nhân nhạy cảm (CCCD, tài khoản ngân hàng) - sau khi đã mask
- Hợp đồng, điều khoản đặc biệt với đối tác
- Thông tin M&A, kế hoạch mở rộng chưa công bố

**Ai được truy cập:** Chỉ manager trở lên, hoặc được phân quyền cụ thể theo role.

---

## 3. QUY TẮC GÁN LABEL

### 3.1. Nguyên tắc chung

| Nguyên tắc | Giải thích |
|-------------|------------|
| Default = [Nội bộ] | Nếu không chắc chắn, gán [Nội bộ]. An toàn hơn [Công khai]. |
| Nâng cấp, không hạ cấp | Khi file chứa MIX nhiều mức, gán mức CAO NHẤT. |
| Label đi theo dữ liệu | Khi extract/copy data, label phải đi cùng. |
| Review định kỳ | Label cần được review mỗi quý (hoặc khi có thay đổi). |

### 3.2. Quy tắc theo loại file

| Loại file | Label mặc định | Điều kiện nâng/hạ |
|-----------|----------------|-------------------|
| Báo giá (Quotation) | [Công khai] | Nâng [Hạn chế] nếu có giá gốc/margin |
| Hóa đơn (Invoice) | [Nội bộ] | Nâng [Hạn chế] nếu có chiết khấu đặc biệt |
| Biên bản họp (Meeting Minutes) | [Nội bộ] | Nâng [Hạn chế] nếu thảo luận chiến lược giá/M&A |
| Ghi chú hệ thống (Notes) | [Nội bộ] | Hạ [Công khai] nếu chỉ là specs kỹ thuật công khai |
| Đơn hàng (Purchase/Sales Order) | [Nội bộ] | Nâng [Hạn chế] nếu có điều khoản đặc biệt |
| Credit Note | [Nội bộ] | Nâng [Hạn chế] nếu có lý do nội bộ |
| Phiếu giao hàng (Delivery Note) | [Công khai] | Giữ [Công khai] vì khách hàng cũng nhận |

### 3.3. Quy tắc theo trường dữ liệu (CSV/database)

| Trường dữ liệu | Label | Ghi chú |
|-----------------|-------|---------|
| account_id, contact_name, role | [Nội bộ] | Thông tin CRM cơ bản |
| phone (đã mask) | [Nội bộ] | Đã qua Gate 3 PII mask |
| email (@company) | [Công khai] | Business contact |
| email (cá nhân, đã mask) | [Nội bộ] | Đã mask nhưng vẫn internal |
| tax_number (MST DN) | [Công khai] | MST doanh nghiệp là thông tin công khai |
| unit_price, cost_price | [Hạn chế] | Thông tin giá nhạy cảm |
| margin, discount_rate | [Hạn chế] | Bí mật kinh doanh |
| credit_limit, outstanding_debt | [Hạn chế] | Thông tin tài chính |

---

## 4. TRIỂN KHAI KỸ THUẬT

### 4.1. Thêm cột access_level vào CSV

Theo yêu cầu Mục 6, mỗi file CSV đi vào pipeline cần có cột `access_level`.

```
account_id,contact_name,...,access_level
SN-001,Nguyễn Văn An,...,noi_bo
SN-002,Công ty ABC,...,cong_khai
```

Giá trị hợp lệ: `cong_khai`, `noi_bo`, `han_che`

### 4.2. Metadata cho PDF

Mỗi PDF sau khi qua pipeline sẽ có metadata file đi kèm:

```json
{
  "file": "Bien_ban_hop_01.pdf",
  "access_level": "noi_bo",
  "labeled_by": "auto/gate4",
  "labeled_at": "2026-11-15T10:00:00",
  "review_due": "2027-02-15"
}
```

### 4.3. Pre-retrieval filtering (ARC 03)

Khi AI Briefing Assistant nhận câu hỏi:
1. Xác định role/quyền của user đang hỏi
2. Lọc chỉ lấy documents/rows có access_level ≤ quyền user
3. Trả kết quả chỉ từ data đã lọc

```
User role: sales_rep    → Chỉ thấy [Công khai] + [Nội bộ]
User role: manager      → Thấy [Công khai] + [Nội bộ] + [Hạn chế]
User role: external     → Chỉ thấy [Công khai]
```

---

## 5. QUY TRÌNH REVIEW & CẬP NHẬT

1. **Tự động gán label** khi file đi qua Gate 4 (dựa trên bảng 3.2 và 3.3)
2. **Data Owner review** label trong 5 ngày làm việc sau khi upload
3. **Review định kỳ** mỗi quý - kiểm tra label còn phù hợp không
4. **Escalation**: Nếu không chắc label → mặc định [Nội bộ] → report cho Data Owner

---

## 6. PHỤ LỤC

### A. Mapping với yêu cầu RFP

| Yêu cầu RFP | Section trong policy | Ghi chú |
|--------------|---------------------|---------|
| SEC 03 - Business Secrecy | Section 2.3 [Hạn chế] | Định nghĩa dữ liệu bí mật KD |
| ARC 03 - Pre-retrieval Filtering | Section 4.3 | Cách lọc theo quyền user |
| Mục 6 - Access labels | Section 2 (toàn bộ) | 3 mức label |
| Mục 6 - CSV access_level | Section 4.1 | Cột access_level |
| SEC 02 - Personal data | Section 3.3 | PII fields → [Nội bộ] sau mask |

### B. Changelog

| Ngày | Phiên bản | Thay đổi |
|------|-----------|----------|
| 15/11/2026 | 1.0 | Phiên bản đầu tiên |
