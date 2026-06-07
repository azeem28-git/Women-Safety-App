from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, SOSHistory, EmergencyContact, IncidentReport
from datetime import datetime

sos_bp = Blueprint('sos', __name__)

@sos_bp.route('/sos/history')
@login_required
def sos_history():
    history = SOSHistory.query.filter_by(user_id=current_user.id).order_by(SOSHistory.triggered_at.desc()).all()
    return render_template('sos/history.html', history=history)

@sos_bp.route('/sos/trigger', methods=['POST'])
@login_required
def trigger_sos():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    address = data.get('address', 'Location not available')

    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()

    sos = SOSHistory(
        user_id=current_user.id,
        latitude=lat,
        longitude=lng,
        address=address,
        contacts_notified=len(contacts),
        status='sent'
    )
    db.session.add(sos)
    db.session.commit()

    contact_list = [{'name': c.name, 'phone': c.phone, 'email': c.email} for c in contacts]

    return jsonify({
        'success': True,
        'sos_id': sos.id,
        'contacts_notified': len(contacts),
        'contacts': contact_list,
        'message': f'SOS alert sent to {len(contacts)} contact(s)!'
    })

@sos_bp.route('/sos/resolve/<int:sos_id>', methods=['POST'])
@login_required
def resolve_sos(sos_id):
    sos = SOSHistory.query.filter_by(id=sos_id, user_id=current_user.id).first_or_404()
    sos.status = 'resolved'
    sos.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'SOS marked as resolved.'})


incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/incidents')
@login_required
def list_incidents():
    incidents = IncidentReport.query.filter_by(user_id=current_user.id).order_by(IncidentReport.reported_at.desc()).all()
    return render_template('incidents/list.html', incidents=incidents)

@incidents_bp.route('/incidents/report', methods=['GET', 'POST'])
@login_required
def report_incident():
    if request.method == 'POST':
        incident_type = request.form.get('incident_type', '').strip()
        description = request.form.get('description', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location_address = request.form.get('location_address', '').strip()
        severity = request.form.get('severity', 'medium')

        if not incident_type or not description:
            flash('Incident type and description are required.', 'danger')
            return render_template('incidents/report.html')

        report = IncidentReport(
            user_id=current_user.id,
            incident_type=incident_type,
            description=description,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            location_address=location_address,
            severity=severity
        )
        db.session.add(report)
        db.session.commit()
        flash('Incident reported successfully. Thank you for helping keep the community safe.', 'success')
        return redirect(url_for('incidents.list_incidents'))

    return render_template('incidents/report.html')

@incidents_bp.route('/incidents/<int:incident_id>')
@login_required
def view_incident(incident_id):
    incident = IncidentReport.query.filter_by(id=incident_id, user_id=current_user.id).first_or_404()
    return render_template('incidents/detail.html', incident=incident)
