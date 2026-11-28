"""
Account Search & Briefing Routes matching the sequence diagram:
- Search accounts by legal_name, tax_code, industry
- Account Briefing endpoint with Authorization check (HTTP 200 vs HTTP 403)
"""
from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthorizationService
from app.utils.audit import record_audit_log, get_recent_audit_logs
from app.utils.security import sanitize_search_query

account_bp = Blueprint("accounts", __name__, url_prefix="/api/accounts")

# Realistic enterprise dummy accounts matching database/init.sql
MOCK_ACCOUNTS = [
    {
        "id": "acc-001",
        "legal_name": "Tập đoàn Công nghệ Viễn thông An Phát",
        "tax_code": "0102345678",
        "industry": "Công nghệ thông tin & Viễn thông",
        "status": "ACTIVE",
        "has_permission": True,
        "sites": [
            {"id": "site-101", "site_name": "Trụ sở chính Cầu Giấy, Hà Nội", "address": "Số 18 Phạm Hùng, Q. Cầu Giấy, Hà Nội"},
            {"id": "site-102", "site_name": "Chi nhánh miền Trung", "address": "Số 45 Nguyễn Văn Linh, Q. Hải Châu, TP. Đà Nẵng"},
            {"id": "site-103", "site_name": "Trung tâm R&D TP.HCM", "address": "Công viên phần mềm Quang Trung, Q. 12, TP.HCM"}
        ],
        "briefing_preview": {
            "summary": "Khách hàng cấp Enterprise, có 12 hợp đồng đang thực hiện, 3 dự án nâng cấp hạ tầng mạng.",
            "citations_count": 4,
            "freshness": "Cập nhật hôm nay 14:30 (Đồng bộ ERP/PDF)",
            "risk_level": "LOW"
        }
    },
    {
        "id": "acc-002",
        "legal_name": "Công ty Cổ phần Sản xuất & Thương mại Đại Dương",
        "tax_code": "0309876543",
        "industry": "Sản xuất & Logistics công nghiệp",
        "status": "ACTIVE",
        "has_permission": True,
        "sites": [
            {"id": "site-201", "site_name": "Nhà máy chính KCN Tân Bình", "address": "Đường CN13, KCN Tân Bình, TP.HCM"},
            {"id": "site-202", "site_name": "Tổng kho logistics Bình Dương", "address": "Đại lộ Bình Dương, TP. Thuận An, Bình Dương"}
        ],
        "briefing_preview": {
            "summary": "Doanh thu năm nay đạt 45 tỷ VND. Đang đàm phán hợp đồng cung ứng giai đoạn 2026-2027.",
            "citations_count": 3,
            "freshness": "Cập nhật 2 ngày trước",
            "risk_level": "MEDIUM"
        }
    },
    {
        "id": "acc-003",
        "legal_name": "Tổng Công ty Dược phẩm Quốc tế Medico",
        "tax_code": "0105558888",
        "industry": "Y tế & Dược phẩm sinh học",
        "status": "ACTIVE",
        "has_permission": True,
        "sites": [
            {"id": "site-301", "site_name": "Trụ sở Đống Đa", "address": "Số 102 Tôn Thất Tùng, Đống Đa, Hà Nội"},
            {"id": "site-302", "site_name": "Chi nhánh Cần Thơ", "address": "Số 20 Trần Phú, Ninh Kiều, Cần Thơ"}
        ],
        "briefing_preview": {
            "summary": "Nhà cung cấp thiết bị y tế chuẩn GMP. Có 2 báo giá cần phê duyệt gia hạn.",
            "citations_count": 5,
            "freshness": "Cập nhật 5 giờ trước",
            "risk_level": "LOW"
        }
    },
    {
        "id": "acc-revoked-004",
        "legal_name": "Công ty TNHH Năng lượng Tái tạo SunPower Việt Nam",
        "tax_code": "0401122334",
        "industry": "Năng lượng & Điện mặt trời",
        "status": "INACTIVE",
        "has_permission": False,  # Permission revoked in sequence diagram
        "sites": [
            {"id": "site-401", "site_name": "Văn phòng Nha Trang", "address": "Số 5 Pasteur, TP. Nha Trang, Khánh Hòa"}
        ],
        "briefing_preview": {
            "summary": "Tài khoản bị hạn chế quyền truy cập.",
            "citations_count": 0,
            "freshness": "Không khả dụng",
            "risk_level": "RESTRICTED"
        }
    },
    {
        "id": "acc-005",
        "legal_name": "Công ty Cổ phần Bán lẻ Tiêu dùng Toàn Cầu",
        "tax_code": "0313456789",
        "industry": "Bán lẻ & Chuỗi siêu thị",
        "status": "ACTIVE",
        "has_permission": True,
        "sites": [
            {"id": "site-501", "site_name": "Văn phòng Quận 1", "address": "Tòa nhà Bitexco, Q. 1, TP.HCM"}
        ],
        "briefing_preview": {
            "summary": "Chuỗi bán lẻ với 60 điểm phân phối toàn quốc. Đang triển khai tích hợp POS số.",
            "citations_count": 2,
            "freshness": "Cập nhật ngày hôm qua",
            "risk_level": "LOW"
        }
    }
]


@account_bp.route("/search", methods=["GET"])
def search_accounts():
    """
    Search accounts by query string (name, tax code, industry).
    Returns list of matched accounts or empty list.
    """
    query = sanitize_search_query(request.args.get("query", ""))
    
    # If no query provided, return all available mock accounts for exploration
    if not query:
        return jsonify({
            "success": True,
            "total": len(MOCK_ACCOUNTS),
            "data": MOCK_ACCOUNTS,
            "message": "Danh sách toàn bộ tài khoản doanh nghiệp."
        }), 200

    q_lower = query.lower()
    matched = [
        acc for acc in MOCK_ACCOUNTS
        if q_lower in acc["legal_name"].lower()
        or q_lower in acc["tax_code"].lower()
        or q_lower in acc["industry"].lower()
    ]

    return jsonify({
        "success": True,
        "query": query,
        "total": len(matched),
        "data": matched,
        "message": f"Tìm thấy {len(matched)} tài khoản phù hợp." if matched else "Không tìm thấy tài khoản phù hợp."
    }), 200


@account_bp.route("/<account_id>/briefing", methods=["GET"])
def get_account_briefing(account_id: str):
    """
    Endpoint demonstrating the Sequence Diagram flow:
    1. Briefing Orchestrator -> Authorization Service: Recheck current permissions
    2. Authorization Service -> PostgreSQL: Verify latest permission status
    3. Alt:
       - [Permission revoked]:
         Authorization Service -> Access revoked
         Briefing Orchestrator -> Block result
         Backend API -> HTTP 403
         Frontend -> Display access revoked
       - [Permission still valid]:
         Authorization Service -> Permission valid
         Briefing Orchestrator -> Record generation and validation events
         Audit Service -> Save audit log
         Save Briefing Draft + citations
         Backend API -> HTTP 200
         Frontend -> Display Briefing and warnings
         Bottom: 'No automatic write-back to CRM / ERP'
    """
    user_id = request.headers.get("X-User-Id", "usr-002")

    # Step 1 & 2: Recheck current permissions
    is_allowed, auth_result = AuthorizationService.recheck_permissions(user_id, account_id)

    # Find the target account
    target_account = next((acc for acc in MOCK_ACCOUNTS if acc["id"] == account_id), None)
    if not target_account:
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": "Không tìm thấy tài khoản với mã đã chỉ định."
        }), 404

    # ALT BRANCH 1: Permission revoked -> Return HTTP 403
    if not is_allowed:
        record_audit_log(
            user_id=user_id,
            action="BRIEFING_ACCESS_REVOKED_BLOCKED",
            resource_type="ACCOUNT",
            resource_id=account_id,
            metadata={
                "reason": auth_result["reason"],
                "account_name": target_account["legal_name"]
            }
        )
        return jsonify({
            "success": False,
            "status": "ACCESS_REVOKED",
            "status_code": 403,
            "error": "HTTP 403 - Access Revoked",
            "message": "Quyền truy cập tài khoản đã bị thu hồi hoặc bạn không có quyền trong phạm vi tài khoản này (Account Scope).",
            "diagram_step": "Display access revoked",
            "account": {
                "id": target_account["id"],
                "legal_name": target_account["legal_name"],
                "tax_code": target_account["tax_code"]
            }
        }), 403

    # ALT BRANCH 2: Permission still valid -> Return HTTP 200 with Briefing & Warnings
    record_audit_log(
        user_id=user_id,
        action="BRIEFING_GENERATION_RECORDED",
        resource_type="ACCOUNT",
        resource_id=account_id,
        metadata={
            "account_name": target_account["legal_name"],
            "validation_status": "VALID",
            "citations_saved": 3
        }
    )

    briefing_payload = {
        "id": f"brf-{account_id}",
        "account_id": account_id,
        "legal_name": target_account["legal_name"],
        "tax_code": target_account["tax_code"],
        "industry": target_account["industry"],
        "status": target_account["status"],
        "briefing_status": "COMPLETED",
        "freshness_status": "Dữ liệu hợp đồng và tài chính đồng bộ trong 24 giờ qua.",
        "validation_status": "VALID",
        "sections": {
            "company_overview": f"{target_account['legal_name']} là doanh nghiệp tiêu biểu trong ngành {target_account['industry']}. Hệ thống quản lý hiện diện tại các địa điểm: {', '.join(s['site_name'] for s in target_account.get('sites', []))}.",
            "commercial_summary": "Tổng giá trị giao dịch ghi nhận: 45,200,000,000 VND qua 12 đơn hàng/hợp đồng. Tỷ lệ hoàn thành đúng hạn 98.5%.",
            "risk_warnings": [
                "Cảnh báo NFR: Không có hành vi tự động ghi ngược (No automatic write-back to CRM / ERP).",
                "Trích dẫn hợp đồng PDF số 2026-HD-08 cần kiểm tra chữ ký số trước khi gia hạn."
            ]
        },
        "citations": [
            {
                "citation_number": 1,
                "claim_text": "Doanh thu năm gần nhất đạt tăng trưởng 18.2%",
                "source_type": "COMMERCIAL",
                "validation_status": "VALID",
                "source_excerpt": "Trích xuất từ bảng commercial_records (Hệ thống ERP)"
            },
            {
                "citation_number": 2,
                "claim_text": "Địa điểm nhà máy chính đáp ứng tiêu chuẩn an toàn công nghiệp",
                "source_type": "PDF",
                "validation_status": "VALID",
                "source_excerpt": "Trích xuất từ file Bien_ban_nghiem_thu_2026.pdf (Trang 4)"
            }
        ],
        "system_notice": "Tuân thủ nghiêm ngặt: No automatic write-back to CRM / ERP"
    }

    return jsonify({
        "success": True,
        "status": "PERMISSION_VALID",
        "status_code": 200,
        "message": "Tải bản tóm tắt hồ sơ khách hàng 360 thành công.",
        "data": briefing_payload
    }), 200


@account_bp.route("/audit-logs", methods=["GET"])
def get_audit_logs():
    """Endpoint to inspect recent audit events from the diagram."""
    logs = get_recent_audit_logs()
    return jsonify({
        "success": True,
        "total": len(logs),
        "data": logs
    }), 200
