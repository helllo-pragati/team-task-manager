"""Task API routes."""
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.task import Task
from app.models.project import ProjectMember
from app.utils.decorators import project_member_required, project_admin_required
from app.utils.validators import VALID_TASK_STATUSES, VALID_TASK_PRIORITIES

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
@project_member_required
def list_tasks(project_id, membership):
    """List all tasks in a project."""
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    assigned_to_filter = request.args.get('assigned_to')

    query = Task.query.filter_by(project_id=project_id)

    if status_filter and status_filter in VALID_TASK_STATUSES:
        query = query.filter_by(status=status_filter)
    if priority_filter and priority_filter in VALID_TASK_PRIORITIES:
        query = query.filter_by(priority=priority_filter)
    if assigned_to_filter:
        try:
            query = query.filter_by(assigned_to=int(assigned_to_filter))
        except ValueError:
            pass

    tasks = query.order_by(Task.created_at.desc()).all()

    return jsonify({
        'tasks': [t.to_dict() for t in tasks]
    }), 200


@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
@project_member_required
def create_task(project_id, membership):
    """Create a new task in a project."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Task title is required'}), 400
    if len(title) > 300:
        return jsonify({'error': 'Task title must be at most 300 characters'}), 400

    description = data.get('description', '').strip()
    status = data.get('status', 'todo')
    priority = data.get('priority', 'medium')
    assigned_to = data.get('assigned_to')
    due_date_str = data.get('due_date')

    # Validate enums
    if status not in VALID_TASK_STATUSES:
        return jsonify({'error': f'Status must be one of: {", ".join(VALID_TASK_STATUSES)}'}), 400
    if priority not in VALID_TASK_PRIORITIES:
        return jsonify({'error': f'Priority must be one of: {", ".join(VALID_TASK_PRIORITIES)}'}), 400

    # Validate assignee is a project member
    if assigned_to:
        member = ProjectMember.query.filter_by(
            project_id=project_id, user_id=assigned_to
        ).first()
        if not member:
            return jsonify({'error': 'Assigned user is not a member of this project'}), 400

    # Parse due date
    due_date = None
    if due_date_str:
        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid due date format. Use YYYY-MM-DD'}), 400

    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        project_id=project_id,
        assigned_to=assigned_to,
        created_by=user_id,
        due_date=due_date
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        'message': 'Task created successfully',
        'task': task.to_dict()
    }), 201


@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get task details."""
    user_id = int(get_jwt_identity())
    task = Task.query.get_or_404(task_id)

    # Check membership
    membership = ProjectMember.query.filter_by(
        project_id=task.project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this project'}), 403

    return jsonify({'task': task.to_dict()}), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task (admin or assignee)."""
    user_id = int(get_jwt_identity())
    task = Task.query.get_or_404(task_id)

    # Check membership and permissions
    membership = ProjectMember.query.filter_by(
        project_id=task.project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this project'}), 403

    # Only admin or assignee can update
    if membership.role != 'admin' and task.assigned_to != user_id:
        return jsonify({'error': 'Only project admins or the assignee can update this task'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # Update fields
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'Task title cannot be empty'}), 400
        task.title = title

    if 'description' in data:
        task.description = data['description'].strip()

    if 'status' in data:
        if data['status'] not in VALID_TASK_STATUSES:
            return jsonify({'error': f'Status must be one of: {", ".join(VALID_TASK_STATUSES)}'}), 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] not in VALID_TASK_PRIORITIES:
            return jsonify({'error': f'Priority must be one of: {", ".join(VALID_TASK_PRIORITIES)}'}), 400
        task.priority = data['priority']

    if 'assigned_to' in data:
        if membership.role != 'admin':
            return jsonify({'error': 'Only admins can reassign tasks'}), 403
        assigned_to = data['assigned_to']
        if assigned_to is not None:
            member = ProjectMember.query.filter_by(
                project_id=task.project_id, user_id=assigned_to
            ).first()
            if not member:
                return jsonify({'error': 'Assigned user is not a member of this project'}), 400
        task.assigned_to = assigned_to

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = date.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'error': 'Invalid due date format. Use YYYY-MM-DD'}), 400
        else:
            task.due_date = None

    db.session.commit()

    return jsonify({
        'message': 'Task updated successfully',
        'task': task.to_dict()
    }), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task (admin only)."""
    user_id = int(get_jwt_identity())
    task = Task.query.get_or_404(task_id)

    membership = ProjectMember.query.filter_by(
        project_id=task.project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this project'}), 403
    if membership.role != 'admin':
        return jsonify({'error': 'Only project admins can delete tasks'}), 403

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'}), 200


@tasks_bp.route('/tasks/<int:task_id>/status', methods=['PATCH'])
@jwt_required()
def update_task_status(task_id):
    """Quick update task status (admin or assignee)."""
    user_id = int(get_jwt_identity())
    task = Task.query.get_or_404(task_id)

    membership = ProjectMember.query.filter_by(
        project_id=task.project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this project'}), 403

    if membership.role != 'admin' and task.assigned_to != user_id:
        return jsonify({'error': 'Only project admins or the assignee can update status'}), 403

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status field is required'}), 400

    if data['status'] not in VALID_TASK_STATUSES:
        return jsonify({'error': f'Status must be one of: {", ".join(VALID_TASK_STATUSES)}'}), 400

    task.status = data['status']
    db.session.commit()

    return jsonify({
        'message': 'Task status updated',
        'task': task.to_dict()
    }), 200
