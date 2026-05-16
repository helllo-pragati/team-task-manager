/* ===== Team Task Manager — Frontend JavaScript ===== */

const API = {
  baseUrl: '',
  getToken() { return localStorage.getItem('token'); },
  setToken(t) { localStorage.setItem('token', t); },
  clearToken() { localStorage.removeItem('token'); localStorage.removeItem('user'); },
  getUser() { try { return JSON.parse(localStorage.getItem('user')); } catch { return null; } },
  setUser(u) { localStorage.setItem('user', JSON.stringify(u)); },

  async request(url, options = {}) {
    const token = this.getToken();
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
      const res = await fetch(this.baseUrl + url, { ...options, headers });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 401) { this.clearToken(); window.location.href = '/login'; return; }
        throw new Error(data.error || 'Something went wrong');
      }
      return data;
    } catch (err) {
      if (err.message !== 'Failed to fetch') throw err;
      throw new Error('Network error. Please try again.');
    }
  },

  get(url) { return this.request(url); },
  post(url, body) { return this.request(url, { method: 'POST', body: JSON.stringify(body) }); },
  put(url, body) { return this.request(url, { method: 'PUT', body: JSON.stringify(body) }); },
  patch(url, body) { return this.request(url, { method: 'PATCH', body: JSON.stringify(body) }); },
  delete(url) { return this.request(url, { method: 'DELETE' }); }
};

/* ===== Auth Functions ===== */
function requireAuth() {
  if (!API.getToken()) { window.location.href = '/login'; return false; }
  return true;
}

function setupSidebar() {
  const user = API.getUser();
  if (!user) return;
  const nameEl = document.getElementById('user-display-name');
  const roleEl = document.getElementById('user-display-role');
  const avatarEl = document.getElementById('user-display-avatar');
  if (nameEl) nameEl.textContent = user.username;
  if (roleEl) roleEl.textContent = user.role;
  if (avatarEl) avatarEl.textContent = user.username.substring(0, 2).toUpperCase();

  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', () => { API.clearToken(); window.location.href = '/login'; });

  // Active nav
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href === '/' && path === '/') item.classList.add('active');
    else if (href !== '/' && path.startsWith(href)) item.classList.add('active');
  });

  // Mobile toggle
  const toggle = document.getElementById('mobile-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  }
}

/* ===== Toast Notifications ===== */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}

/* ===== Auth Pages ===== */
async function handleSignup(e) {
  e.preventDefault();
  const alertEl = document.getElementById('signup-alert');
  const btn = e.target.querySelector('button[type="submit"]');
  const username = document.getElementById('signup-username').value.trim();
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const role = document.querySelector('.role-option.selected')?.dataset.role || 'member';

  if (!username || !email || !password) {
    alertEl.textContent = 'All fields are required';
    alertEl.style.display = 'block'; return;
  }

  btn.disabled = true; btn.textContent = 'Creating account...';
  try {
    const data = await API.post('/api/auth/signup', { username, email, password, role });
    API.setToken(data.access_token);
    API.setUser(data.user);
    window.location.href = '/';
  } catch (err) {
    alertEl.textContent = err.message;
    alertEl.style.display = 'block';
    btn.disabled = false; btn.textContent = 'Create Account';
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const alertEl = document.getElementById('login-alert');
  const btn = e.target.querySelector('button[type="submit"]');
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  if (!email || !password) {
    alertEl.textContent = 'All fields are required';
    alertEl.style.display = 'block'; return;
  }

  btn.disabled = true; btn.textContent = 'Signing in...';
  try {
    const data = await API.post('/api/auth/login', { email, password });
    API.setToken(data.access_token);
    API.setUser(data.user);
    window.location.href = '/';
  } catch (err) {
    alertEl.textContent = err.message;
    alertEl.style.display = 'block';
    btn.disabled = false; btn.textContent = 'Sign In';
  }
}

/* ===== Dashboard ===== */
async function loadDashboard() {
  if (!requireAuth()) return;
  setupSidebar();
  try {
    const data = await API.get('/api/dashboard');
    renderDashboardStats(data.stats);
    renderOverdueTasks(data.overdue_tasks);
    renderRecentTasks(data.recent_tasks);
  } catch (err) { showToast(err.message, 'error'); }
}

function renderDashboardStats(stats) {
  const grid = document.getElementById('stats-grid');
  if (!grid) return;
  grid.innerHTML = `
    <div class="stat-card purple fade-in"><div class="stat-value">${stats.total_projects}</div><div class="stat-label">Projects</div></div>
    <div class="stat-card blue fade-in"><div class="stat-value">${stats.total_tasks}</div><div class="stat-label">Total Tasks</div></div>
    <div class="stat-card cyan fade-in"><div class="stat-value">${stats.my_tasks}</div><div class="stat-label">My Tasks</div></div>
    <div class="stat-card orange fade-in"><div class="stat-value">${stats.in_progress}</div><div class="stat-label">In Progress</div></div>
    <div class="stat-card green fade-in"><div class="stat-value">${stats.done}</div><div class="stat-label">Completed</div></div>
    <div class="stat-card red fade-in"><div class="stat-value">${stats.overdue}</div><div class="stat-label">Overdue</div></div>
  `;
}

function renderOverdueTasks(tasks) {
  const container = document.getElementById('overdue-list');
  if (!container) return;
  if (tasks.length === 0) {
    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">✅</div><div class="empty-state-title">No overdue tasks</div></div>';
    return;
  }
  container.innerHTML = tasks.map(t => `
    <div class="overdue-item fade-in">
      <div>
        <div class="overdue-item-title">${escapeHtml(t.title)}</div>
        <div class="overdue-item-meta">${escapeHtml(t.project_name || '')} · Due: ${t.due_date}</div>
      </div>
      <span class="badge badge-high">Overdue</span>
    </div>
  `).join('');
}

function renderRecentTasks(tasks) {
  const container = document.getElementById('recent-tasks');
  if (!container) return;
  if (tasks.length === 0) {
    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📋</div><div class="empty-state-title">No tasks yet</div></div>';
    return;
  }
  container.innerHTML = `<table><thead><tr><th>Task</th><th>Project</th><th>Status</th><th>Priority</th></tr></thead><tbody>
    ${tasks.map(t => `<tr>
      <td>${escapeHtml(t.title)}</td>
      <td>${escapeHtml(t.project_name || '')}</td>
      <td><span class="badge badge-${t.status}">${formatStatus(t.status)}</span></td>
      <td><span class="badge badge-${t.priority}">${t.priority}</span></td>
    </tr>`).join('')}
  </tbody></table>`;
}

/* ===== Projects Page ===== */
async function loadProjects() {
  if (!requireAuth()) return;
  setupSidebar();
  try {
    const data = await API.get('/api/projects');
    renderProjects(data.projects);
  } catch (err) { showToast(err.message, 'error'); }
}

function renderProjects(projects) {
  const grid = document.getElementById('projects-grid');
  if (!grid) return;
  if (projects.length === 0) {
    grid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📁</div><div class="empty-state-title">No projects yet</div><div class="empty-state-desc">Create your first project to get started</div></div>';
    return;
  }
  grid.innerHTML = projects.map(p => {
    const stats = p.task_stats || { total: 0, todo: 0, in_progress: 0, done: 0 };
    return `
    <div class="project-card fade-in" onclick="window.location.href='/projects/${p.id}'">
      <div class="project-card-title">${escapeHtml(p.name)}</div>
      <div class="project-card-desc">${escapeHtml(p.description || 'No description')}</div>
      <div class="project-card-stats">
        <div class="project-stat"><div class="project-stat-value">${stats.total}</div><div class="project-stat-label">Tasks</div></div>
        <div class="project-stat"><div class="project-stat-value" style="color:var(--info)">${stats.todo}</div><div class="project-stat-label">To Do</div></div>
        <div class="project-stat"><div class="project-stat-value" style="color:var(--warning)">${stats.in_progress}</div><div class="project-stat-label">Active</div></div>
        <div class="project-stat"><div class="project-stat-value" style="color:var(--success)">${stats.done}</div><div class="project-stat-label">Done</div></div>
      </div>
      <div class="project-card-footer"><span>By ${escapeHtml(p.creator_name || '')}</span><span>${formatDate(p.created_at)}</span></div>
    </div>`;
  }).join('');
}

async function createProject() {
  const name = document.getElementById('project-name').value.trim();
  const desc = document.getElementById('project-desc').value.trim();
  if (!name) { showToast('Project name is required', 'error'); return; }
  try {
    await API.post('/api/projects', { name, description: desc });
    showToast('Project created!');
    closeModal('create-project-modal');
    loadProjects();
  } catch (err) { showToast(err.message, 'error'); }
}

/* ===== Project Detail ===== */
let currentProject = null;
let currentUserRole = 'member';

async function loadProjectDetail(projectId) {
  if (!requireAuth()) return;
  setupSidebar();
  try {
    const data = await API.get(`/api/projects/${projectId}`);
    currentProject = data.project;
    currentUserRole = data.user_role;
    renderProjectHeader(data.project);
    await loadProjectTasks(projectId);
    if (currentUserRole === 'admin') {
      document.querySelectorAll('.admin-only').forEach(el => el.style.display = '');
    }
  } catch (err) { showToast(err.message, 'error'); }
}

function renderProjectHeader(project) {
  const el = document.getElementById('project-title');
  const descEl = document.getElementById('project-description');
  if (el) el.textContent = project.name;
  if (descEl) descEl.textContent = project.description || '';
}

async function loadProjectTasks(projectId) {
  try {
    const data = await API.get(`/api/projects/${projectId}/tasks`);
    renderKanban(data.tasks);
  } catch (err) { showToast(err.message, 'error'); }
}

function renderKanban(tasks) {
  const cols = { todo: [], in_progress: [], done: [] };
  tasks.forEach(t => { if (cols[t.status]) cols[t.status].push(t); });

  ['todo', 'in_progress', 'done'].forEach(status => {
    const body = document.getElementById(`kanban-${status}`);
    const count = document.getElementById(`count-${status}`);
    if (count) count.textContent = cols[status].length;
    if (!body) return;
    if (cols[status].length === 0) {
      body.innerHTML = '<div class="empty-state" style="padding:24px"><div style="color:var(--text-muted);font-size:0.8rem">No tasks</div></div>';
      return;
    }
    body.innerHTML = cols[status].map(t => `
      <div class="task-card fade-in" draggable="true" data-task-id="${t.id}" data-status="${t.status}"
           ondragstart="onDragStart(event)" ondragend="onDragEnd(event)">
        <div class="task-card-title">${escapeHtml(t.title)}</div>
        ${t.description ? `<div class="task-card-desc">${escapeHtml(t.description)}</div>` : ''}
        <div class="task-card-meta">
          <span class="badge badge-${t.priority}">${t.priority}</span>
          ${t.assignee_name ? `<span class="assignee-tag"><span class="assignee-mini-avatar">${t.assignee_name.substring(0,2).toUpperCase()}</span>${escapeHtml(t.assignee_name)}</span>` : ''}
        </div>
        ${t.due_date ? `<div class="due-date ${t.is_overdue ? 'overdue' : ''}" style="margin-top:8px">📅 ${t.due_date}${t.is_overdue ? ' (Overdue!)' : ''}</div>` : ''}
      </div>
    `).join('');
  });

  // Setup drop zones
  document.querySelectorAll('.kanban-column-body').forEach(col => {
    col.addEventListener('dragover', e => { e.preventDefault(); col.style.background = 'var(--bg-card)'; });
    col.addEventListener('dragleave', () => { col.style.background = ''; });
    col.addEventListener('drop', e => onDrop(e, col));
  });
}

/* ===== Drag & Drop ===== */
let draggedTaskId = null;

function onDragStart(e) {
  draggedTaskId = e.target.dataset.taskId;
  e.target.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
}

function onDragEnd(e) { e.target.classList.remove('dragging'); }

async function onDrop(e, col) {
  e.preventDefault();
  col.style.background = '';
  const newStatus = col.dataset.status;
  if (!draggedTaskId || !newStatus) return;
  try {
    await API.patch(`/api/tasks/${draggedTaskId}/status`, { status: newStatus });
    await loadProjectTasks(currentProject.id);
    showToast('Task status updated');
  } catch (err) { showToast(err.message, 'error'); }
}

/* ===== Create Task ===== */
async function createTask() {
  if (!currentProject) return;
  const title = document.getElementById('task-title').value.trim();
  const desc = document.getElementById('task-desc').value.trim();
  const priority = document.getElementById('task-priority').value;
  const assignedTo = document.getElementById('task-assignee').value;
  const dueDate = document.getElementById('task-due-date').value;

  if (!title) { showToast('Task title is required', 'error'); return; }

  try {
    await API.post(`/api/projects/${currentProject.id}/tasks`, {
      title, description: desc, priority,
      assigned_to: assignedTo ? parseInt(assignedTo) : null,
      due_date: dueDate || null
    });
    showToast('Task created!');
    closeModal('create-task-modal');
    await loadProjectTasks(currentProject.id);
  } catch (err) { showToast(err.message, 'error'); }
}

/* ===== Members ===== */
async function loadMembers() {
  if (!currentProject) return;
  try {
    const data = await API.get(`/api/projects/${currentProject.id}/members`);
    renderMembers(data.members);
    populateAssigneeSelect(data.members);
  } catch (err) { showToast(err.message, 'error'); }
}

function renderMembers(members) {
  const list = document.getElementById('members-list');
  if (!list) return;
  list.innerHTML = members.map(m => `
    <div class="member-item fade-in">
      <div class="member-avatar">${(m.username || '').substring(0,2).toUpperCase()}</div>
      <div class="member-info">
        <div class="member-name">${escapeHtml(m.username || '')}</div>
        <div class="member-email">${escapeHtml(m.email || '')}</div>
      </div>
      <span class="badge badge-${m.role}">${m.role}</span>
      ${currentUserRole === 'admin' ? `<button class="btn btn-sm btn-danger" onclick="removeMember(${m.user_id})" style="margin-left:auto">Remove</button>` : ''}
    </div>
  `).join('');
}

function populateAssigneeSelect(members) {
  const select = document.getElementById('task-assignee');
  if (!select) return;
  select.innerHTML = '<option value="">Unassigned</option>' +
    members.map(m => `<option value="${m.user_id}">${escapeHtml(m.username)}</option>`).join('');
}

async function addMember() {
  if (!currentProject) return;
  const email = document.getElementById('member-email').value.trim();
  const role = document.getElementById('member-role').value;
  if (!email) { showToast('Email is required', 'error'); return; }
  try {
    await API.post(`/api/projects/${currentProject.id}/members`, { email, role });
    showToast('Member added!');
    closeModal('add-member-modal');
    loadMembers();
  } catch (err) { showToast(err.message, 'error'); }
}

async function removeMember(userId) {
  if (!currentProject || !confirm('Remove this member?')) return;
  try {
    await API.delete(`/api/projects/${currentProject.id}/members/${userId}`);
    showToast('Member removed');
    loadMembers();
  } catch (err) { showToast(err.message, 'error'); }
}

async function deleteProject() {
  if (!currentProject || !confirm('Delete this project and all its tasks?')) return;
  try {
    await API.delete(`/api/projects/${currentProject.id}`);
    showToast('Project deleted');
    window.location.href = '/projects';
  } catch (err) { showToast(err.message, 'error'); }
}

/* ===== Modals ===== */
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('active');
  if (id === 'create-task-modal' && currentProject) loadMembers();
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) { modal.classList.remove('active'); modal.querySelectorAll('input,textarea,select').forEach(el => { if (el.type !== 'hidden') el.value = ''; }); }
}

/* ===== Helpers ===== */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatStatus(s) { return s === 'in_progress' ? 'In Progress' : s === 'todo' ? 'To Do' : 'Done'; }

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/* ===== Role Selector ===== */
document.addEventListener('click', e => {
  if (e.target.closest('.role-option')) {
    document.querySelectorAll('.role-option').forEach(o => o.classList.remove('selected'));
    e.target.closest('.role-option').classList.add('selected');
  }
  // Close modal on overlay click
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});
