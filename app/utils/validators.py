"""Input validation helpers."""
import re


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """Validate password strength. Returns (is_valid, message)."""
    if len(password) < 6:
        return False, 'Password must be at least 6 characters long'
    return True, 'Valid'


def validate_username(username):
    """Validate username format. Returns (is_valid, message)."""
    if len(username) < 3:
        return False, 'Username must be at least 3 characters long'
    if len(username) > 80:
        return False, 'Username must be at most 80 characters long'
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, 'Username can only contain letters, numbers, and underscores'
    return True, 'Valid'


VALID_TASK_STATUSES = ['todo', 'in_progress', 'done']
VALID_TASK_PRIORITIES = ['low', 'medium', 'high']
VALID_ROLES = ['admin', 'member']
