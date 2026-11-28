"""
Audit service helper to record system events and validation checks.
Matches the sequence diagram: 'Record generation and validation events' -> 'Save audit log'
"""
from datetime import datetime, timezone
from typing import Dict, Any, List

# In-memory storage for static mock audit logs
AUDIT_LOG_STORE: List[Dict[str, Any]] = []


def record_audit_log(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    ip_address: str = "127.0.0.1",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Record an audit log entry in compliance with SDS NFR and the sequence diagram.
    """
    log_entry = {
        "id": f"audit-{len(AUDIT_LOG_STORE) + 1:04d}",
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    AUDIT_LOG_STORE.append(log_entry)
    print(f"[AUDIT SERVICE] Action: {action} | Resource: {resource_type}:{resource_id} | User: {user_id}")
    return log_entry


def get_recent_audit_logs(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve the most recent audit logs."""
    return list(reversed(AUDIT_LOG_STORE[-limit:]))
