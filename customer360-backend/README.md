# TASK: Thiết kế giao diện Đăng nhập và Tìm kiếm tài khoản

## 1. Mục tiêu
Thực hiện task thiết kế giao diện tĩnh cho hai màn hình:
- Màn hình Đăng nhập (Login).
- Màn hình Tìm kiếm tài khoản (Account Search).

Căn cứ thực hiện: SDS Mục 7 – Giai đoạn 1 (M7-M8).

## 2. Công nghệ bắt buộc
- Backend: Python.
- Frontend: JavaScript (Node.js), HTML5 và CSS3.
- Giao diện cần thiết kế rõ ràng, hiện đại, dễ sử dụng và tương thích với màn hình máy tính.
- Tổ chức source code thành các thư mục riêng biệt giữa Backend và Frontend.

## 3. Phạm vi chức năng

### 3.1. Màn hình Đăng nhập
Thiết kế giao diện bao gồm:
- Tiêu đề Đăng nhập.
- Ô nhập tên tài khoản hoặc email.
- Ô nhập mật khẩu.
- Nút hiển thị/ẩn mật khẩu.
- Nút Đăng nhập.
- Liên kết chuyển đến màn hình Tìm kiếm tài khoản (nếu phù hợp với SDS).
- Hiển thị thông báo lỗi giao diện khi bỏ trống thông tin.

### 3.2. Màn hình Tìm kiếm tài khoản
Thiết kế giao diện bao gồm:
- Tiêu đề Tìm kiếm tài khoản.
- Ô nhập thông tin tìm kiếm.
- Nút Tìm kiếm.
- Khu vực hiển thị kết quả tìm kiếm.
- Trạng thái không tìm thấy tài khoản.
- Nút quay lại màn hình Đăng nhập.

## 4. Yêu cầu giao diện (UI/UX)
- Thiết kế giao diện chuyên nghiệp, tối giản.
- Bố cục cân đối, màu sắc đồng nhất giữa hai màn hình.
- Có thể sử dụng Card, Shadow, Border Radius.
- Có hiệu ứng Hover cho các nút.
- Có kiểm tra dữ liệu nhập ở mức giao diện.
- Responsive trên máy tính và điện thoại.
- Không sử dụng dữ liệu cá nhân thật.

## 5. Yêu cầu kỹ thuật
- Backend viết bằng Python, sử dụng Flask nếu phù hợp với cấu trúc dự án.
- Frontend sử dụng JavaScript và Node.js để quản lý môi trường chạy.
- Code phải rõ ràng, dễ đọc, dễ bảo trì.
- Phân chia component và file hợp lý.
- Không viết toàn bộ chương trình vào một file.
- Không tự ý bổ sung chức năng ngoài phạm vi SDS.
- Không triển khai xác thực thực tế, cơ sở dữ liệu hoặc xử lý nghiệp vụ phức tạp nếu SDS chỉ yêu cầu giao diện tĩnh.

## 6. Yêu cầu đầu ra
1. Hoàn thành giao diện Đăng nhập.
2. Hoàn thành giao diện Tìm kiếm tài khoản.
3. Hai màn hình có thể chuyển đổi qua lại.
4. Có đầy đủ source code Python và JavaScript.
5. Có file README hướng dẫn cài đặt và chạy dự án.
6. Kiểm tra và sửa toàn bộ lỗi trước khi bàn giao.
7. Đảm bảo dự án chạy được trên máy tính Windows.

## 7. Quy trình thực hiện
- Bước 1: Kiểm tra cấu trúc source code hiện tại.
- Bước 2: Đọc SDS Mục 7 (M7-M8) để xác định yêu cầu chính xác.
- Bước 3: Xác định phạm vi và thiết kế giao diện.
- Bước 4: Tiến hành lập trình Backend Python và Frontend JavaScript.
- Bước 5: Kiểm tra giao diện và khả năng chuyển đổi giữa hai màn hình.
- Bước 6: Chạy thử toàn bộ dự án và khắc phục lỗi.
- Bước 7: Tổng kết các file đã tạo, chức năng đã hoàn thành và hướng dẫn chạy.

## 8. Tiêu chí nghiệm thu
- Hai màn hình Đăng nhập và Tìm kiếm tài khoản được thiết kế hoàn chỉnh.
- Giao diện hoạt động đúng theo phạm vi SDS.
- Không phát sinh chức năng ngoài yêu cầu.
- Source code sạch, dễ hiểu, dễ bảo trì.
- Dự án chạy thành công.
- Có hướng dẫn chạy và kiểm thử rõ ràng.

**Lưu ý quan trọng:** Trước khi lập trình, hãy kiểm tra tài liệu SDS và source code hiện tại. Nếu có điểm nào chưa được quy định trong SDS, hãy ghi nhận và hỏi lại thay vì tự suy diễn hoặc tự bổ sung yêu cầu.

---

## 9. Báo cáo hoàn thành & Hướng dẫn chạy dự án

### 9.1. Cấu trúc Source Code đã tổ chức
```
Cust360-brief/
├── customer360-backend/           # Backend Python (Flask)
│   ├── app/
│   │   ├── __init__.py            # Flask app factory, CORS & phục vụ static
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py     # API đăng nhập & kiểm tra validation
│   │   │   └── account_routes.py  # API tìm kiếm & Briefing theo sơ đồ SDS
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── auth_service.py    # Authorization Service kiểm tra quyền (HTTP 200 vs 403)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py        # Kiểm tra dữ liệu đăng nhập & query
│   │       └── audit.py           # Audit Service ghi nhật ký truy cập theo sơ đồ
│   ├── database/
│   │   └── init.sql               # Khởi tạo CSDL chuẩn (Users, Accounts, Sites, Citations, Audit)
│   ├── requirements.txt           # Thư viện Flask, Flask-Cors
│   ├── run.py                     # Entry point khởi chạy Backend (Port 5000)
│   └── README.md
│
├── customer360-frontend/          # Frontend JavaScript (Node.js), HTML5, CSS3
│   ├── package.json               # Cấu hình scripts Node.js
│   ├── server.js                  # Web Server Node.js (Zero-dependency, Port 3000)
│   ├── public/
│   │   ├── index.html             # Khung giao diện chính (SPA Container)
│   │   ├── css/
│   │   │   ├── variables.css      # Hệ thống màu sắc thương hiệu Customer 360, shadows, radius
│   │   │   ├── base.css           # Header, typography, badge người dùng, toast notifications
│   │   │   ├── login.css          # Giao diện card đăng nhập, icon, toggle password, error banner
│   │   │   ├── search.css         # Thanh tìm kiếm, bộ lọc nhanh, grid kết quả, empty state
│   │   │   ├── modal.css          # Modal hiển thị tóm tắt Briefing và cảnh báo theo sơ đồ
│   │   │   └── responsive.css     # Tương thích màn hình máy tính và thiết bị di động
│   │   └── js/
│   │       ├── app.js             # Bộ điều hướng chuyển màn hình (Router) & Quản lý User State
│   │       ├── services/
│   │       │   └── api.js         # Kết nối API Backend (kèm fallback tĩnh độc lập)
│   │       └── components/
│   │           ├── login.js       # Component Đăng nhập, validate bỏ trống, điền nhanh demo
│   │           ├── search.js      # Component Tìm kiếm tài khoản, xử lý rẽ nhánh sơ đồ 200/403
│   │           └── toast.js       # Component thông báo Toast hiện đại
│   └── src/
│       └── types/
│           ├── auth.ts            # Kiểu dữ liệu xác thực & phân quyền
│           └── briefing.ts        # Kiểu dữ liệu tài khoản, địa điểm, trích dẫn PDF/ERP
│
├── run_backend.bat                # Script 1-click chạy Backend trên Windows
├── run_frontend.bat               # Script 1-click chạy Frontend trên Windows
└── README.md                      # Hướng dẫn tổng quan
```

### 9.2. Thể hiện sơ đồ tuần tự (Sequence Diagram) trong thiết kế
Dự án phản ánh chính xác luồng hoạt động trong ảnh sơ đồ kiến trúc:
1. **Frontend $\leftrightarrow$ Backend API:** Gửi yêu cầu truy vấn thông tin tài khoản và yêu cầu tạo bản tóm tắt hồ sơ (Customer 360 Briefing).
2. **Briefing Orchestrator $\leftrightarrow$ Authorization Service:** Tái kiểm tra quyền người dùng (`Recheck current permissions`) đối chiếu trạng thái cấp quyền tài khoản (`Verify latest permission status`).
3. **Rẽ nhánh điều kiện (alt):**
   - **Nhánh `[Permission revoked]`:** 
     - Authorization Service phản hồi `Access revoked`.
     - Briefing Orchestrator thực hiện `Block result`.
     - Backend API trả về mã **HTTP 403 Forbidden**.
     - Frontend kích hoạt trạng thái **Display access revoked**: hiển thị hộp thoại cảnh báo quyền truy cập bị thu hồi/từ chối, đồng thời ghi log qua Audit Service.
     - *(Có thể kiểm tra trực tiếp bằng tài khoản mẫu: Công ty TNHH Năng lượng Tái tạo SunPower Việt Nam)*.
   - **Nhánh `[Permission still valid]`:**
     - Authorization Service phản hồi `Permission valid`.
     - Audit Service lưu nhật ký (`Record generation and validation events` $\rightarrow$ `Save audit log`).
     - Briefing Orchestrator lưu bản nháp tóm tắt kèm trích dẫn (`Save Briefing Draft + citations`).
     - Backend API trả về mã **HTTP 200 OK**.
     - Frontend kích hoạt trạng thái **Display Briefing and warnings**: hiển thị thông tin doanh nghiệp, số liệu thương mại, trích dẫn bằng chứng PDF / ERP và các cảnh báo rủi ro.
4. **Quy định an toàn dữ liệu:** Hệ thống hiển thị rõ ràng thông báo tuân thủ: *"No automatic write-back to CRM / ERP"* (Không tự ý ghi ngược dữ liệu vào hệ thống lõi).

### 9.3. Hướng dẫn chạy dự án trên Windows

#### Cách 1: Chạy bằng file .bat (Tiện lợi nhất)
- Chạy Backend: Nhấp đúp vào file `run_backend.bat`
- Chạy Frontend: Nhấp đúp vào file `run_frontend.bat`
- Truy cập trình duyệt tại: `http://localhost:3000`

#### Cách 2: Chạy thủ công qua Terminal / PowerShell

**Bước 1: Khởi chạy Backend (Python Flask)**
```powershell
cd customer360-backend
python -m pip install -r requirements.txt
python run.py
```
> Backend API sẽ lắng nghe tại: `http://127.0.0.1:5000` (Kiểm tra sức khỏe: `http://127.0.0.1:5000/api/health`)

**Bước 2: Khởi chạy Frontend (Node.js)**
Mở một cửa sổ Terminal mới:
```powershell
cd customer360-frontend
npm start
# hoặc: node server.js
```
> Mở trình duyệt và truy cập: `http://localhost:3000`

### 9.4. Hướng dẫn kiểm thử giao diện
1. **Kiểm tra Màn hình Đăng nhập:**
   - Để trống ô tên tài khoản hoặc mật khẩu và bấm **Đăng nhập** $\rightarrow$ Giao diện hiển thị viền đỏ và thông báo lỗi rõ ràng.
   - Nhập mật khẩu và bấm vào icon **Con mắt** $\rightarrow$ Mật khẩu chuyển đổi giữa ẩn (`••••••`) và hiển thị văn bản rõ ràng.
   - Bấm vào các nút tài khoản mẫu (SALES, ADMIN, SERVICE) để tự động điền nhanh.
   - Bấm liên kết *"Chuyển nhanh đến màn hình Tìm kiếm tài khoản"* $\rightarrow$ Chuyển ngay sang màn hình Tìm kiếm.
   - Bấm nút **Đăng nhập** sau khi điền thông tin $\rightarrow$ Hiển thị Toast thông báo thành công và chuyển mượt mà sang màn hình Tìm kiếm.
2. **Kiểm tra Màn hình Tìm kiếm tài khoản:**
   - Ô tìm kiếm hỗ trợ tra cứu thời gian thực theo tên công ty (ví dụ: *An Phát*, *Đại Dương*, *Medico*), mã số thuế hoặc ngành nghề.
   - Bấm nút **✕** trên ô tìm kiếm để xóa nhanh nội dung tìm kiếm.
   - Bấm các nút bộ lọc nhanh (CNTT & Viễn thông, Sản xuất, Y tế & Dược phẩm, Bán lẻ...).
   - Nhập từ khóa không tồn tại (ví dụ: `xyz999`) $\rightarrow$ Giao diện hiển thị **Empty State** thông báo không tìm thấy kết quả cùng nút xem lại tất cả tài khoản.
   - Bấm nút **Quay lại Đăng nhập** hoặc nút **Đăng xuất** ở Header $\rightarrow$ Quay lại màn hình Đăng nhập.
3. **Kiểm tra luồng Sơ đồ Sequence Diagram:**
   - Bấm *"Xem tóm tắt hồ sơ (Customer 360)"* tại tài khoản **Tập đoàn Công nghệ Viễn thông An Phát** $\rightarrow$ Minh họa nhánh **HTTP 200 (Permission valid)**, hiển thị Briefing, bằng chứng trích dẫn PDF/ERP và cảnh báo.
   - Bấm *"Xem tóm tắt hồ sơ (Customer 360)"* tại tài khoản **Công ty TNHH Năng lượng Tái tạo SunPower Việt Nam** $\rightarrow$ Minh họa nhánh **HTTP 403 (Permission revoked)**, hiển thị cảnh báo đỏ *"Display access revoked: Quyền truy cập tài khoản đã bị thu hồi"*.
