"""Dashboard API route."""
from datetime import date
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.project import ProjectMember, Project
from app.models.task import Task

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get dashboard statistics for the current user."""
    user_id = int(get_jwt_identity())

    memberships = ProjectMember.query.filter_by(user_id=user_id).all()
    project_ids = [m.project_id for m in memberships]

    all_tasks = Task.query.filter(Task.project_id.in_(project_ids)).all() if project_ids else []
    my_tasks = [t for t in all_tasks if t.assigned_to == user_id]

    today = date.today()
    overdue_tasks = [
        t for t in all_tasks
        if t.due_date and t.due_date < today and t.status != 'done'
    ]
    recent_tasks = sorted(all_tasks, key=lambda t: t.created_at or '', reverse=True)[:10]
    projects = Project.query.filter(Project.id.in_(project_ids)).all() if project_ids else []

    return jsonify({
        'stats': {
            'total_projects': len(project_ids),
            'total_tasks': len(all_tasks),
            'my_tasks': len(my_tasks),
            'todo': sum(1 for t in all_tasks if t.status == 'todo'),
            'in_progress': sum(1 for t in all_tasks if t.status == 'in_progress'),
            'done': sum(1 for t in all_tasks if t.status == 'done'),
            'overdue': len(overdue_tasks)
        },
        'overdue_tasks': [t.to_dict() for t in overdue_tasks],
        'recent_tasks': [t.to_dict() for t in recent_tasks],
        'projects': [p.to_dict(include_stats=True) for p in projects]
    }), 200
