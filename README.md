# Customer 360 Briefing Tool - Giai đoạn 1 (M7-M8)

Hệ thống tóm tắt hồ sơ khách hàng doanh nghiệp 360 độ (Customer 360) và quản lý phạm vi phân quyền truy cập (Account Scope).

---

## 1. Công nghệ sử dụng
- **Backend:** Python (Flask, Flask-CORS) - Cung cấp RESTful API và phục vụ các dịch vụ xác thực, kiểm tra quyền theo SDS.
- **Frontend:** JavaScript (Node.js runtime), HTML5, CSS3 - Giao diện hiện đại, responsive, phân chia component rõ ràng.

---

## 2. Các chức năng đã hoàn thành

### 2.1. Màn hình Đăng nhập (Login)
- Tiêu đề và nhận diện thương hiệu Customer 360 Enterprise.
- Ô nhập tên tài khoản hoặc email kèm icon trực quan.
- Ô nhập mật khẩu kèm nút hiển thị/ẩn mật khẩu (Show/Hide Password).
- Kiểm tra tính hợp lệ dữ liệu ở mức giao diện (báo lỗi viền đỏ và banner khi bỏ trống thông tin).
- Nút bấm Đăng nhập với hiệu ứng hover, shadow, loading.
- Liên kết chuyển nhanh đến màn hình Tìm kiếm tài khoản.
- Nút chọn nhanh tài khoản mẫu cho các vai trò: **ADMIN**, **SALES**, **SERVICE**.

### 2.2. Màn hình Tìm kiếm tài khoản (Account Search)
- Thanh tìm kiếm thời gian thực theo tên công ty, mã số thuế (MST) hoặc ngành nghề.
- Nút xóa nhanh nội dung và các thẻ lọc nhanh theo ngành (CNTT, Sản xuất, Y tế, Bán lẻ, Năng lượng).
- Danh thiếp hồ sơ công ty hiển thị đầy đủ: Tên pháp lý, Mã số thuế, Ngành nghề, Địa điểm/Chi nhánh, Trạng thái hoạt động.
- Trạng thái không tìm thấy kết quả (**Empty State**) thiết kế đẹp mắt kèm nút đặt lại tìm kiếm.
- Nút quay lại màn hình Đăng nhập và nút Đăng xuất trên thanh điều hướng Header.

### 2.3. Hiện thực hóa Sơ đồ tuần tự (Sequence Diagram)
- **Tái kiểm tra quyền (Authorization Service & Briefing Orchestrator):**
  - **Nhánh `[Permission revoked]` (HTTP 403):** Chặn dữ liệu nhạy cảm, hiển thị cảnh báo *"Display access revoked: Quyền truy cập tài khoản đã bị thu hồi hoặc bị hạn chế theo chính sách phân quyền Account Scope"*, ghi nhận vào Audit Log. *(Thử nghiệm với tài khoản SunPower)*.
  - **Nhánh `[Permission still valid]` (HTTP 200):** Hiển thị bản tóm tắt hồ sơ 360, trích dẫn bằng chứng PDF và đơn hàng ERP (Citations), trạng thái độ mới (Freshness status) và các cảnh báo rủi ro (Risk warnings). *(Thử nghiệm với tài khoản An Phát, Đại Dương, Medico)*.
  - **Tuân thủ quy tắc kiến trúc:** Hiển thị thông báo *"No automatic write-back to CRM / ERP"*.

---

## 3. Hướng dẫn khởi chạy trên máy tính Windows

### Cách 1: Khởi chạy nhanh bằng File Batch (Khuyên dùng)
1. Chạy Backend: Nhấp đúp vào file `run_backend.bat`
2. Chạy Frontend: Nhấp đúp vào file `run_frontend.bat`
3. Mở trình duyệt web và truy cập: [http://localhost:3000](http://localhost:3000)

### Cách 2: Khởi chạy bằng dòng lệnh Terminal / PowerShell

**1. Khởi chạy Backend:**
```powershell
cd customer360-backend
python -m pip install -r requirements.txt
python run.py
```
*Backend chạy tại:* `http://127.0.0.1:5000`

**2. Khởi chạy Frontend:**
```powershell
cd customer360-frontend
node server.js
```
*Frontend chạy tại:* `http://localhost:3000`
