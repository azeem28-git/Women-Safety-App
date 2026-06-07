from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, EmergencyContact, SOSHistory

api_bp = Blueprint('api', __name__)

@api_bp.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'email': c.email,
        'relationship': c.relationship,
        'is_primary': c.is_primary
    } for c in contacts])

@api_bp.route('/sos/active', methods=['GET'])
@login_required
def get_active_sos():
    active = SOSHistory.query.filter_by(user_id=current_user.id, status='sent').order_by(SOSHistory.triggered_at.desc()).first()
    if active:
        return jsonify({
            'active': True,
            'sos_id': active.id,
            'triggered_at': active.triggered_at.isoformat(),
            'latitude': active.latitude,
            'longitude': active.longitude
        })
    return jsonify({'active': False})

@api_bp.route('/user/stats', methods=['GET'])
@login_required
def user_stats():
    sos_count = SOSHistory.query.filter_by(user_id=current_user.id).count()
    contacts_count = EmergencyContact.query.filter_by(user_id=current_user.id).count()
    return jsonify({
        'sos_count': sos_count,
        'contacts_count': contacts_count,
        'user_name': current_user.full_name
    })
