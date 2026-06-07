from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, EmergencyContact

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts')
@login_required
def list_contacts():
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).order_by(EmergencyContact.is_primary.desc()).all()
    return render_template('contacts/list.html', contacts=contacts)

@contacts_bp.route('/contacts/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        relationship = request.form.get('relationship', '').strip()
        email = request.form.get('email', '').strip()
        is_primary = request.form.get('is_primary') == 'on'

        if not name or not phone or not relationship:
            flash('Name, phone, and relationship are required.', 'danger')
            return render_template('contacts/form.html', action='Add', contact=None)

        existing_count = EmergencyContact.query.filter_by(user_id=current_user.id).count()
        if existing_count >= 10:
            flash('You can add a maximum of 10 emergency contacts.', 'warning')
            return redirect(url_for('contacts.list_contacts'))

        if is_primary:
            EmergencyContact.query.filter_by(user_id=current_user.id, is_primary=True).update({'is_primary': False})

        contact = EmergencyContact(
            user_id=current_user.id,
            name=name,
            phone=phone,
            relationship=relationship,
            email=email,
            is_primary=is_primary
        )
        db.session.add(contact)
        db.session.commit()
        flash(f'Contact {name} added successfully!', 'success')
        return redirect(url_for('contacts.list_contacts'))

    return render_template('contacts/form.html', action='Add', contact=None)

@contacts_bp.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        contact.name = request.form.get('name', '').strip()
        contact.phone = request.form.get('phone', '').strip()
        contact.relationship = request.form.get('relationship', '').strip()
        contact.email = request.form.get('email', '').strip()
        is_primary = request.form.get('is_primary') == 'on'

        if is_primary and not contact.is_primary:
            EmergencyContact.query.filter_by(user_id=current_user.id, is_primary=True).update({'is_primary': False})
        contact.is_primary = is_primary

        db.session.commit()
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('contacts.list_contacts'))

    return render_template('contacts/form.html', action='Edit', contact=contact)

@contacts_bp.route('/contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    name = contact.name
    db.session.delete(contact)
    db.session.commit()
    flash(f'Contact {name} deleted.', 'info')
    return redirect(url_for('contacts.list_contacts'))
