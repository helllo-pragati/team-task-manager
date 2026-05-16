"""Role-based access control decorators."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.project import ProjectMember


def project_member_required(f):
    """Decorator to ensure the current user is a member of the project."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = int(get_jwt_identity())
        project_id = kwargs.get('project_id')

        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400

        membership = ProjectMember.query.filter_by(
            project_id=project_id, user_id=user_id
        ).first()

        if not membership:
            return jsonify({'error': 'You are not a member of this project'}), 403

        kwargs['membership'] = membership
        return f(*args, **kwargs)

    return decorated_function


def project_admin_required(f):
    """Decorator to ensure the current user is an admin of the project."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = int(get_jwt_identity())
        project_id = kwargs.get('project_id')

        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400

        membership = ProjectMember.query.filter_by(
            project_id=project_id, user_id=user_id
        ).first()

        if not membership:
            return jsonify({'error': 'You are not a member of this project'}), 403

        if membership.role != 'admin':
            return jsonify({'error': 'Admin access required for this action'}), 403

        kwargs['membership'] = membership
        return f(*args, **kwargs)

    return decorated_function
