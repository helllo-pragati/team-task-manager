"""Project and ProjectMember models."""
from datetime import datetime, timezone
from app import db


class Project(db.Model):
    """Project model."""

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    members = db.relationship('ProjectMember', backref='project', lazy='dynamic',
                               cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy='dynamic',
                             cascade='all, delete-orphan')

    def to_dict(self, include_members=False, include_stats=False):
        """Serialize project to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_members:
            data['members'] = [m.to_dict() for m in self.members.all()]
        if include_stats:
            all_tasks = self.tasks.all()
            data['task_stats'] = {
                'total': len(all_tasks),
                'todo': sum(1 for t in all_tasks if t.status == 'todo'),
                'in_progress': sum(1 for t in all_tasks if t.status == 'in_progress'),
                'done': sum(1 for t in all_tasks if t.status == 'done')
            }
        return data


class ProjectMember(db.Model):
    """Association model for project membership with roles."""

    __tablename__ = 'project_members'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # 'admin' or 'member'
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user = db.relationship('User', backref='project_memberships')

    # Unique constraint: a user can only be a member of a project once
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='unique_project_member'),
    )

    def to_dict(self):
        """Serialize project member to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'email': self.user.email if self.user else None,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
