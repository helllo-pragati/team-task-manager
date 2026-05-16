"""Project API routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.utils.decorators import project_member_required, project_admin_required

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    """List all projects the current user is a member of."""
    user_id = int(get_jwt_identity())

    memberships = ProjectMember.query.filter_by(user_id=user_id).all()
    project_ids = [m.project_id for m in memberships]

    projects = Project.query.filter(Project.id.in_(project_ids)).order_by(
        Project.created_at.desc()
    ).all()

    return jsonify({
        'projects': [p.to_dict(include_stats=True) for p in projects]
    }), 200


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not name:
        return jsonify({'error': 'Project name is required'}), 400

    if len(name) > 200:
        return jsonify({'error': 'Project name must be at most 200 characters'}), 400

    # Create project
    project = Project(name=name, description=description, created_by=user_id)
    db.session.add(project)
    db.session.flush()  # Get project.id

    # Add creator as admin member
    member = ProjectMember(project_id=project.id, user_id=user_id, role='admin')
    db.session.add(member)
    db.session.commit()

    return jsonify({
        'message': 'Project created successfully',
        'project': project.to_dict(include_members=True, include_stats=True)
    }), 201


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
@project_member_required
def get_project(project_id, membership):
    """Get project details."""
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'project': project.to_dict(include_members=True, include_stats=True),
        'user_role': membership.role
    }), 200


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
@project_admin_required
def update_project(project_id, membership):
    """Update project details (admin only)."""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'Project name cannot be empty'}), 400
        if len(name) > 200:
            return jsonify({'error': 'Project name must be at most 200 characters'}), 400
        project.name = name

    if 'description' in data:
        project.description = data['description'].strip()

    db.session.commit()

    return jsonify({
        'message': 'Project updated successfully',
        'project': project.to_dict(include_members=True, include_stats=True)
    }), 200


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
@project_admin_required
def delete_project(project_id, membership):
    """Delete a project (admin only)."""
    project = Project.query.get_or_404(project_id)

    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': 'Project deleted successfully'}), 200


# --- Member Management ---

@projects_bp.route('/<int:project_id>/members', methods=['GET'])
@jwt_required()
@project_member_required
def list_members(project_id, membership):
    """List all members of a project."""
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    return jsonify({
        'members': [m.to_dict() for m in members]
    }), 200


@projects_bp.route('/<int:project_id>/members', methods=['POST'])
@jwt_required()
@project_admin_required
def add_member(project_id, membership):
    """Add a member to the project (admin only)."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # Accept either user_id or email
    user = None
    if 'user_id' in data:
        user = User.query.get(data['user_id'])
    elif 'email' in data:
        user = User.query.filter_by(email=data['email'].strip().lower()).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check if already a member
    existing = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user.id
    ).first()
    if existing:
        return jsonify({'error': 'User is already a member of this project'}), 409

    role = data.get('role', 'member')
    if role not in ('admin', 'member'):
        return jsonify({'error': 'Role must be admin or member'}), 400

    member = ProjectMember(project_id=project_id, user_id=user.id, role=role)
    db.session.add(member)
    db.session.commit()

    return jsonify({
        'message': f'{user.username} added to project',
        'member': member.to_dict()
    }), 201


@projects_bp.route('/<int:project_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
@project_admin_required
def remove_member(project_id, user_id, membership):
    """Remove a member from the project (admin only)."""
    # Prevent removing yourself if you're the only admin
    if user_id == int(get_jwt_identity()):
        admin_count = ProjectMember.query.filter_by(
            project_id=project_id, role='admin'
        ).count()
        if admin_count <= 1:
            return jsonify({
                'error': 'Cannot remove yourself as the only admin'
            }), 400

    member = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user_id
    ).first()

    if not member:
        return jsonify({'error': 'Member not found'}), 404

    db.session.delete(member)
    db.session.commit()

    return jsonify({'message': 'Member removed successfully'}), 200
