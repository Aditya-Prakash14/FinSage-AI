# backend/utils/privacy.py
"""Privacy and security utilities for financial data"""

import hashlib
import os
from typing import Dict, Any
from datetime import datetime
import json


def anonymize_user_id(user_id: str, salt: str = None) -> str:
    """Hash user ID for privacy-preserving analytics"""
    if salt is None:
        salt = os.getenv("ANONYMIZATION_SALT", "finsage_default_salt")
    
    hash_input = f"{user_id}{salt}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()[:16]


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask PII in data before logging or external calls
    
    Masks: email, phone, names, account numbers
    """
    masked = data.copy()
    
    sensitive_fields = ['email', 'phone', 'name', 'account_number', 'card_number']
    
    for field in sensitive_fields:
        if field in masked:
            if field == 'email':
                masked[field] = _mask_email(masked[field])
            elif field == 'phone':
                masked[field] = _mask_phone(masked[field])
            else:
                masked[field] = "***MASKED***"
    
    return masked


def _mask_email(email: str) -> str:
    """Mask email keeping first 2 chars and domain"""
    if '@' not in email:
        return "***@***.***"
    
    local, domain = email.split('@')
    if len(local) > 2:
        masked_local = local[:2] + "***"
    else:
        masked_local = "***"
    
    return f"{masked_local}@{domain}"


def _mask_phone(phone: str) -> str:
    """Mask phone keeping last 4 digits"""
    phone_digits = ''.join(filter(str.isdigit, phone))
    if len(phone_digits) > 4:
        return "******" + phone_digits[-4:]
    return "***MASKED***"


def create_audit_log(
    action: str,
    user_id: str,
    resource: str,
    metadata: Dict = None
) -> Dict:
    """
    Create audit log entry for compliance
    
    Args:
        action: Action performed (e.g., "create", "read", "update", "delete")
        user_id: User performing action
        resource: Resource accessed (e.g., "transaction", "budget")
        metadata: Additional context
    
    Returns:
        Audit log entry
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": anonymize_user_id(user_id),  # Store anonymized ID
        "resource": resource,
        "metadata": metadata or {},
        "ip_hash": None,  # Could be populated from request context
    }


def sanitize_amount(amount: Any) -> float:
    """Sanitize and validate monetary amount"""
    try:
        value = float(amount)
        # Allow negative amounts for debit transactions
        if abs(value) > 10_000_000:  # 1 crore limit
            raise ValueError("Amount exceeds maximum allowed")
        return round(value, 2)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid amount: {amount}") from e


def encrypt_sensitive_field(data: str, key: str = None) -> str:
    """
    Simple encryption for sensitive fields (use proper encryption in production)
    Note: This is a placeholder - use proper encryption libraries in production
    """
    # In production, use cryptography library with proper key management
    if key is None:
        key = os.getenv("ENCRYPTION_KEY", "dev_key_not_secure")
    
    # Placeholder: base64 encoding (NOT SECURE - use proper encryption)
    import base64
    return base64.b64encode(data.encode()).decode()


def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validate date range for queries"""
    if start_date > end_date:
        raise ValueError("Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise ValueError("Date range cannot exceed 1 year")
    
    return True


def calculate_data_freshness(last_updated: datetime) -> str:
    """Calculate how fresh the data is"""
    now = datetime.utcnow()
    delta = now - last_updated
    
    if delta.days == 0:
        if delta.seconds < 3600:
            return "very_fresh"  # < 1 hour
        else:
            return "fresh"  # < 1 day
    elif delta.days < 7:
        return "recent"  # < 1 week
    elif delta.days < 30:
        return "aging"  # < 1 month
    else:
        return "stale"  # > 1 month
