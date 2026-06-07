from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from models import EmergencyContact, SOSHistory, IncidentReport

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def home():
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    recent_sos = SOSHistory.query.filter_by(user_id=current_user.id).order_by(SOSHistory.triggered_at.desc()).limit(5).all()
    recent_incidents = IncidentReport.query.filter_by(user_id=current_user.id).order_by(IncidentReport.reported_at.desc()).limit(3).all()
    sos_count = SOSHistory.query.filter_by(user_id=current_user.id).count()
    incident_count = IncidentReport.query.filter_by(user_id=current_user.id).count()
    maps_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')

    safety_tips = [
        {"icon": "shield-check", "title": "Stay Alert", "tip": "Always be aware of your surroundings, especially in unfamiliar areas."},
        {"icon": "phone", "title": "Share Location", "tip": "Always share your live location with trusted contacts when traveling alone."},
        {"icon": "people", "title": "Trust Instincts", "tip": "If something feels wrong, trust your gut and remove yourself from the situation."},
        {"icon": "lightbulb", "title": "Well-lit Paths", "tip": "Stick to well-lit, populated routes especially during nighttime."},
        {"icon": "battery-charging", "title": "Keep Phone Charged", "tip": "Always keep your phone charged and have emergency numbers saved."},
        {"icon": "person-running", "title": "Self-Defense", "tip": "Consider learning basic self-defense techniques for personal safety."},
    ]

    return render_template('dashboard/home.html',
        contacts=contacts,
        recent_sos=recent_sos,
        recent_incidents=recent_incidents,
        sos_count=sos_count,
        incident_count=incident_count,
        safety_tips=safety_tips,
        maps_key=maps_key
    )

@dashboard_bp.route('/safety-tips')
@login_required
def safety_tips():
    tips = [
        {
            "category": "Personal Safety",
            "icon": "shield-fill-check",
            "color": "danger",
            "items": [
                "Always be aware of your surroundings.",
                "Trust your instincts — if something feels wrong, it probably is.",
                "Avoid isolated areas, especially at night.",
                "Walk confidently and with purpose.",
                "Carry a personal safety alarm or whistle.",
            ]
        },
        {
            "category": "Digital Safety",
            "icon": "phone-fill",
            "color": "primary",
            "items": [
                "Keep your phone charged at all times.",
                "Save all emergency contacts on speed dial.",
                "Share your live location with trusted family members.",
                "Enable location services for emergency apps.",
                "Avoid sharing your location publicly on social media.",
            ]
        },
        {
            "category": "Travel Safety",
            "icon": "car-front-fill",
            "color": "warning",
            "items": [
                "Inform someone of your travel plans and expected arrival time.",
                "Prefer well-known and reputable transportation services.",
                "Sit in the back seat of cabs and verify the driver's details.",
                "Avoid late-night solo travel whenever possible.",
                "Keep a backup charging power bank with you.",
            ]
        },
        {
            "category": "Emergency Preparedness",
            "icon": "exclamation-triangle-fill",
            "color": "success",
            "items": [
                "Know the local police and emergency service numbers.",
                "Have at least 3 trusted emergency contacts saved.",
                "Learn basic first-aid and self-defense techniques.",
                "Keep cash for emergencies — not just digital payments.",
                "Know the nearest police station or hospital in your area.",
            ]
        },
        {
            "category": "Home Safety",
            "icon": "house-fill",
            "color": "info",
            "items": [
                "Ensure your home has proper locks on all doors and windows.",
                "Never open the door to strangers without verification.",
                "Install a security camera or video doorbell.",
                "Have a code word with family for emergencies.",
                "Keep neighbors informed if you live alone.",
            ]
        },
    ]
    return render_template('dashboard/safety_tips.html', tips=tips)

@dashboard_bp.route('/nearby-police')
@login_required
def nearby_police():
    maps_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('dashboard/nearby_police.html', maps_key=maps_key)
