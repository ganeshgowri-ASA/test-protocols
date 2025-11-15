"""
Input Validators
================
Validation functions for user inputs.
"""

import re


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return True  # Phone is optional

    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Check if it's a valid number (10-15 digits, optionally starting with +)
    pattern = r'^\+?\d{10,15}$'
    return bool(re.match(pattern, cleaned))


def validate_code(code: str) -> bool:
    """
    Validate entity/audit code format

    Args:
        code: Code to validate

    Returns:
        True if valid, False otherwise
    """
    if not code:
        return False

    # Alphanumeric, hyphens, underscores allowed
    # Length between 2 and 50 characters
    pattern = r'^[A-Z0-9_-]{2,50}$'
    return bool(re.match(pattern, code.upper()))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    return True, "Password is strong"


def validate_date_range(start_date, end_date) -> bool:
    """
    Validate that end date is after start date

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        True if valid, False otherwise
    """
    if not start_date or not end_date:
        return False

    return end_date >= start_date


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators and special characters
    sanitized = re.sub(r'[^\w\s\-\.]', '', filename)
    sanitized = sanitized.strip()

    # Limit length
    if len(sanitized) > 200:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:190] + (f'.{ext}' if ext else '')

    return sanitized
