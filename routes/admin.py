from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from models import db, Admin, User, EmergencyContact, SOSHistory, IncidentReport
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin login required.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['admin_name'] = admin.username
            admin.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_sos = SOSHistory.query.count()
    total_incidents = IncidentReport.query.count()
    pending_incidents = IncidentReport.query.filter_by(status='pending').count()
    recent_sos = SOSHistory.query.order_by(SOSHistory.triggered_at.desc()).limit(5).all()
    recent_incidents = IncidentReport.query.order_by(IncidentReport.reported_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_users=total_users,
        active_users=active_users,
        total_sos=total_sos,
        total_incidents=total_incidents,
        pending_incidents=pending_incidents,
        recent_sos=recent_sos,
        recent_incidents=recent_incidents,
        recent_users=recent_users
    )

@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.query
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.phone.ilike(f'%{search}%'))
        )
    users_paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/users.html', users=users_paginated, search=search)

@admin_bp.route('/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.full_name} has been {status}.', 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/incidents')
@admin_required
def incidents():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    severity_filter = request.args.get('severity', '')
    query = IncidentReport.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if severity_filter:
        query = query.filter_by(severity=severity_filter)
    incidents_paginated = query.order_by(IncidentReport.reported_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/incidents.html', incidents=incidents_paginated,
                           status_filter=status_filter, severity_filter=severity_filter)

@admin_bp.route('/incidents/update/<int:incident_id>', methods=['POST'])
@admin_required
def update_incident(incident_id):
    incident = IncidentReport.query.get_or_404(incident_id)
    incident.status = request.form.get('status', incident.status)
    incident.admin_notes = request.form.get('admin_notes', '')
    if incident.status in ('reviewed', 'resolved'):
        incident.reviewed_at = datetime.utcnow()
    db.session.commit()
    flash('Incident updated successfully.', 'success')
    return redirect(url_for('admin.incidents'))

@admin_bp.route('/sos-history')
@admin_required
def sos_history():
    page = request.args.get('page', 1, type=int)
    history = SOSHistory.query.order_by(SOSHistory.triggered_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/sos_history.html', history=history)
