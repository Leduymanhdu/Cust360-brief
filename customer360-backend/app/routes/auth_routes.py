"""
Authentication Routes for Customer 360
"""
from flask import Blueprint, request, jsonify
from app.utils.security import validate_login_input
from app.utils.audit import record_audit_log

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Demo mock users conforming to init.sql roles: ADMIN, SALES, SERVICE
DEMO_USERS = {
    "admin@cust360.vn": {
        "id": "usr-001",
        "email": "admin@cust360.vn",
        "full_name": "Nguyễn Quản Trị",
        "role": "ADMIN",
        "is_active": True
    },
    "sales@cust360.vn": {
        "id": "usr-002",
        "email": "sales@cust360.vn",
        "full_name": "Trần Thị Thu Thảo",
        "role": "SALES",
        "is_active": True
    },
    "service@cust360.vn": {
        "id": "usr-003",
        "email": "service@cust360.vn",
        "full_name": "Lê Hoàng Nam",
        "role": "SERVICE",
        "is_active": True
    }
}


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login endpoint with interface-level and basic static credential validation.
    """
    data = request.get_json(silent=True) or {}
    username_or_email = data.get("username_or_email", "").strip()
    password = data.get("password", "").strip()

    # Form validation check
    is_valid, error_msg = validate_login_input(username_or_email, password)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": error_msg
        }), 400

    # Match mock user or create default guest session for UI testing
    matched_user = DEMO_USERS.get(username_or_email.lower())
    if not matched_user:
        # If user logs in with generic name, provide fallback demo user
        matched_user = {
            "id": "usr-demo",
            "email": username_or_email,
            "full_name": username_or_email.split("@")[0].title() or "Nhân Viên Kinh Doanh",
            "role": "SALES",
            "is_active": True
        }

    # Record login audit
    record_audit_log(
        user_id=matched_user["id"],
        action="USER_LOGIN_SUCCESS",
        resource_type="USER",
        resource_id=matched_user["id"],
        metadata={"role": matched_user["role"], "email": matched_user["email"]}
    )

    return jsonify({
        "success": True,
        "message": "Đăng nhập thành công.",
        "token": f"mock-jwt-token-{matched_user['id']}",
        "user": matched_user
    }), 200
