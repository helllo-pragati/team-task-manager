"""HTML page routes."""
from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def dashboard_page():
    """Serve the dashboard page."""
    return render_template('dashboard.html')


@pages_bp.route('/login')
def login_page():
    """Serve the login page."""
    return render_template('login.html')


@pages_bp.route('/signup')
def signup_page():
    """Serve the signup page."""
    return render_template('signup.html')


@pages_bp.route('/projects')
def projects_page():
    """Serve the projects list page."""
    return render_template('projects.html')


@pages_bp.route('/projects/<int:project_id>')
def project_detail_page(project_id):
    """Serve the project detail page."""
    return render_template('project_detail.html', project_id=project_id)
