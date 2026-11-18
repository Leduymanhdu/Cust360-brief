"""
Security and validation helper utilities.
"""
import re
from typing import Tuple, Optional


def validate_login_input(username_or_email: Optional[str], password: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate login input on the backend side.
    """
    if not username_or_email or not username_or_email.strip():
        return False, "Tên tài khoản hoặc email không được để trống."
    
    if not password or not password.strip():
        return False, "Mật khẩu không được để trống."
    
    clean_username = username_or_email.strip()
    if len(clean_username) < 3:
        return False, "Tên tài khoản hoặc email phải có ít nhất 3 ký tự."
        
    return True, None


def sanitize_search_query(query: Optional[str]) -> str:
    """
    Sanitize search text to prevent basic injection or formatting issues.
    """
    if not query:
        return ""
    # Strip spaces and basic sanitization
    return query.strip()
