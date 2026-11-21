# Customer 360 Briefing Assistant API

Backend FastAPI cho deliverable Swagger API ở Giai đoạn 2 của SDS. OpenAPI có
request/response models, bearer-auth scheme, mô tả lỗi, trạng thái HTTP và ví dụ
để frontend có thể bắt đầu tích hợp bằng dữ liệu mẫu.

> **Chế độ mock:** API lưu file upload xuống đĩa cục bộ và giữ trạng thái import
> trong bộ nhớ. Đăng nhập không phát hành JWT thật; tạo briefing, ghi database và
> xóa cache Redis đều là mô phỏng. Không dùng bản này với dữ liệu khách hàng hoặc
> triển khai production.

## Chạy cục bộ

Yêu cầu Python 3.10 trở lên.

```powershell
cd "D:\project HKDN\Cust360-brief\customer360-backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Mở Swagger UI tại [http://localhost:8000/docs](http://localhost:8000/docs);
ReDoc tại `/redoc`; OpenAPI JSON tại `/openapi.json`.

## Hướng dẫn Swagger cho Frontend

Swagger UI không phải file HTML viết riêng. FastAPI tự sinh tài liệu từ code:

- `app/main.py`: khởi tạo ứng dụng, metadata và đăng ký các router.
- `app/schemas.py`: request/response models dùng để tạo OpenAPI schemas.
- `app/routers/`: endpoint, method, quyền truy cập và response của từng API.
- `/openapi.json`: đặc tả OpenAPI dạng JSON để import vào Postman hoặc công cụ sinh client.

### Thử API trên Swagger UI

1. Chạy backend và mở `http://localhost:8000/docs`.
2. Mở `POST /api/v1/auth/login`, chọn **Try it out**, nhập tài khoản SALES hoặc ADMIN ở phần dưới, rồi chọn **Execute**.
3. Sao chép `access_token` trong response. Chọn **Authorize** ở đầu trang Swagger và nhập token; Swagger tự thêm scheme `Bearer`.
4. Mở `GET /api/v1/accounts/search`, nhập `q=ABC`, rồi chọn **Execute**. API trả về hai kết quả mẫu và `requires_manual_selection: true`; frontend cần để người dùng tự chọn account.
5. Dùng `id` trong kết quả tìm kiếm cho `POST /api/v1/briefings/generate`. `site_id` có thể bỏ qua để tạo briefing cấp công ty. Response `202` trả về `briefing_id`.
6. Dùng `briefing_id` để thử `GET /api/v1/briefings/{briefing_id}`, `GET /api/v1/briefings/{briefing_id}/citations` hoặc `GET /api/v1/briefings/{briefing_id}/export`.
7. Các API trong nhóm **Administration** yêu cầu đăng nhập bằng tài khoản ADMIN. Import CSV/PDF dùng `multipart/form-data`, trả `202` kèm `job_id`; dùng `GET /api/v1/admin/imports/{job_id}` để theo dõi trạng thái import.

### Kết nối từ ứng dụng Frontend

Ví dụ đăng nhập và gọi tìm kiếm bằng `fetch`:

```javascript
const apiBaseUrl = "http://localhost:8000/api/v1";

const loginResponse = await fetch(`${apiBaseUrl}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "sales@songnhat.com.vn",
    password: "SecurePass123!",
  }),
});
const { access_token: accessToken } = await loginResponse.json();

const searchResponse = await fetch(
  `${apiBaseUrl}/accounts/search?q=${encodeURIComponent("ABC")}`,
  { headers: { Authorization: `Bearer ${accessToken}` } },
);
const searchResult = await searchResponse.json();
```

Frontend chạy ở `http://localhost:3000` hoặc `http://localhost:5173` được cho phép mặc định. Nếu dùng origin khác, đặt biến môi trường `CORS_ORIGINS` thành danh sách origin, phân cách bằng dấu phẩy, trước khi chạy API.

## Tài khoản demo

| Role | Email | Password | Token |
| --- | --- | --- | --- |
| SALES | `sales@songnhat.com.vn` | `SecurePass123!` | `demo-sales-token` |
| ADMIN | `admin@songnhat.com.vn` | `AdminPass123!` | `demo-admin-token` |

Gọi `POST /api/v1/auth/login`, sao chép `access_token`, chọn **Authorize** trong
Swagger và nhập token (không cần tự thêm tiền tố `Bearer`).

Sales được truy cập hai account mẫu ABC. Admin được phép truy cập cả ba account.
Tìm kiếm `ABC` trả về hai kết quả và `requires_manual_selection: true`; API không
tự chọn hay gộp account.

## API contract

| Method | Endpoint | Quyền | Mô tả |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Public | Đăng nhập tài khoản demo |
| `GET` | `/api/v1/accounts/search?q=ABC` | Bearer | Tìm account theo tên/mã số thuế trong account scope |
| `POST` | `/api/v1/briefings/generate` | Bearer + account scope | Trả `202` và tạo briefing mẫu |
| `GET` | `/api/v1/briefings/{briefing_id}` | Bearer + account scope | Lấy trạng thái và đủ sáu phần briefing |
| `GET` | `/api/v1/briefings/{briefing_id}/citations` | Bearer + account scope | Lấy citations và trạng thái kiểm tra |
| `GET` | `/api/v1/briefings/{briefing_id}/export` | Bearer + account scope | Tải PDF mock có ghi watermark |
| `POST` | `/api/v1/admin/import/csv` | ADMIN | Kiểm tra, lưu CSV UTF-8 và tạo import job (`202`) |
| `POST` | `/api/v1/admin/import/pdf` | ADMIN | Kiểm tra, lưu PDF và tạo import job (`202`) |
| `GET` | `/api/v1/admin/imports/{job_id}` | ADMIN | Lấy metadata file và trạng thái import |
| `POST` | `/api/v1/admin/users/{user_id}/revoke-access` | ADMIN | Mô phỏng thu hồi account scope |
| `GET` | `/health` | Public | Liveness check |

`BriefingSections` luôn mô tả đủ các key: `account_and_site`,
`contacts_and_roles`, `recent_interactions`, `commercial_facts`,
`service_issues`, `suggested_questions_and_gaps`. Mỗi phần có `content` và
`citations` (mảng số thứ tự citation).

Các lỗi dùng HTTP status theo hợp đồng: `400` dữ liệu không hợp lệ, `401`
chưa xác thực, `403` sai quyền/account scope, `404` không tìm thấy, `413`
file vượt giới hạn dung lượng, `500` không ghi được file lên hệ thống lưu trữ.
Tài liệu endpoint và schema đầy đủ nằm trong Swagger.

## Luồng upload CSV/PDF

Endpoint import nhận `multipart/form-data` với field `file`, kiểm tra và lưu file
theo trình tự sau:

1. **Kiểm tra định dạng khai báo:** phần mở rộng phải là `.csv` (endpoint CSV)
   hoặc `.pdf` (endpoint PDF), và `Content-Type` phải nằm trong danh sách cho
   phép. Sai định dạng trả `400`.
2. **Kiểm tra dung lượng:** file được đọc theo từng chunk và ghi xuống đĩa; vượt
   `MAX_UPLOAD_BYTES` (mặc định `10 MiB`) trả `413` và file dở dang bị xóa.
3. **Lưu trữ:** file được ghi vào `UPLOAD_DIR` (mặc định `var/uploads/<kind>/`)
   với tên sinh tự động theo UUID; metadata lưu tên gốc, `Content-Type`, dung
   lượng và checksum SHA-256. Lỗi ghi đĩa trả `500`.
4. **Kiểm tra nội dung:** chữ ký `%PDF-` với PDF, giải mã UTF-8 và đếm bản ghi
   với CSV. Nội dung sai trả `400` và file đã lưu bị xóa.
5. **Tạo import job:** trả `202` với `job_id`, `status: PENDING` và metadata file.
   Job chuyển sang `PROCESSING` rồi `COMPLETED` (hoặc `FAILED` kèm `error`).
   Frontend dùng `GET /api/v1/admin/imports/{job_id}` để poll trạng thái.

Trạng thái import: `PENDING` → `PROCESSING` → `COMPLETED` / `FAILED`. Trong bản
mock, xử lý nền chỉ xác minh file lưu trữ còn tồn tại và khớp checksum; bước ghi
dữ liệu vào PostgreSQL sẽ thay thế bước này khi ghép nối thật.

Cấu hình bằng biến môi trường trước khi chạy API:

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `MAX_UPLOAD_BYTES` | `10485760` (10 MiB) | Giới hạn dung lượng mỗi file upload |
| `UPLOAD_DIR` | `var/uploads` | Thư mục lưu file đã upload |
| `UPLOAD_CHUNK_SIZE` | `1048576` (1 MiB) | Kích thước mỗi lần đọc khi ghi file |

Bảng `import_jobs` trong `database/init.sql` là schema đích cho metadata và trạng
thái import khi kết nối PostgreSQL.

## Docker

```powershell
docker compose up --build
```

Compose khởi động API, PostgreSQL và Redis để dựng môi trường phát triển. API
mock hiện chưa kết nối tới PostgreSQL/Redis; schema ban đầu nằm tại
`database/init.sql`.

## Kiểm thử

```powershell
pytest -q
```
