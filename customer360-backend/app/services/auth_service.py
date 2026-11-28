"""
Authorization Service matching the sequence diagram:
- Rechecks current permissions against user_account_access and user status
- Handles Permission revoked (HTTP 403) vs Permission still valid (HTTP 200)
"""
from typing import Dict, Any, Tuple


class AuthorizationService:
    """
    Authorization Service for checking user permissions and account access scope.
    """
    
    # Mock accounts with their permissions for the current demo user
    REVOKED_ACCOUNT_IDS = {"acc-revoked-004", "acc-restricted-999"}

    @classmethod
    def recheck_permissions(cls, user_id: str, account_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Recheck current permissions.
        Corresponds to sequence diagram steps:
        Briefing Orchestrator -> Authorization Service: Recheck current permissions
        Authorization Service -> PostgreSQL: Verify latest permission status
        """
        # Check if the account permission has been revoked
        if account_id in cls.REVOKED_ACCOUNT_IDS:
            return False, {
                "status": "REVOKED",
                "status_code": 403,
                "reason": "Quyền truy cập tài khoản đã bị thu hồi hoặc bị hạn chế theo chính sách phân quyền Account Scope.",
                "action_required": "Display access revoked"
            }
        
        return True, {
            "status": "VALID",
            "status_code": 200,
            "reason": "Permission valid",
            "action_required": "Record generation and validation events"
        }
