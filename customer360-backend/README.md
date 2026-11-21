# Customer 360 Briefing Assistant API

Backend FastAPI cho deliverable Swagger API ở Giai đoạn 2 của SDS. OpenAPI có
request/response models, bearer-auth scheme, mô tả lỗi, trạng thái HTTP và ví dụ
để frontend có thể bắt đầu tích hợp bằng dữ liệu mẫu.

> **Chế độ mock:** API hiện dùng dữ liệu trong bộ nhớ. Đăng nhập không phát hành
> JWT thật; import, tạo briefing, ghi database và xóa cache Redis đều là mô phỏng.
> Không dùng bản này với dữ liệu khách hàng hoặc triển khai production.

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
| `POST` | `/api/v1/admin/import/csv` | ADMIN | Kiểm tra CSV UTF-8 và trả import job mẫu |
| `POST` | `/api/v1/admin/import/pdf` | ADMIN | Kiểm tra chữ ký PDF và trả import job mẫu |
| `POST` | `/api/v1/admin/users/{user_id}/revoke-access` | ADMIN | Mô phỏng thu hồi account scope |
| `GET` | `/health` | Public | Liveness check |

`BriefingSections` luôn mô tả đủ các key: `account_and_site`,
`contacts_and_roles`, `recent_interactions`, `commercial_facts`,
`service_issues`, `suggested_questions_and_gaps`. Mỗi phần có `content` và
`citations` (mảng số thứ tự citation).

Các lỗi dùng HTTP status theo hợp đồng: `400` dữ liệu không hợp lệ, `401`
chưa xác thực, `403` sai quyền/account scope, `404` không tìm thấy, `413`
file vượt giới hạn 10 MiB. Tài liệu endpoint và schema đầy đủ nằm trong Swagger.

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
