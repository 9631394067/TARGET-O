import os
import qrcode
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Event

bookings = Blueprint('bookings', __name__)

def generate_qr(booking):
    qr_data = f"EventFlow|REF:{booking.booking_ref}|EVENT:{booking.event.title}|TICKETS:{booking.tickets_count}|NAME:{booking.attendee_name}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#7c3aed", back_color="white")
    qr_filename = f"qr_{booking.booking_ref}.png"
    qr_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'qrcodes', qr_filename)
    img.save(qr_path)
    return f"qrcodes/{qr_filename}"

@bookings.route('/book/<int:event_id>', methods=['GET', 'POST'])
@login_required
def book(event_id):
    event = Event.query.get_or_404(event_id)
    if event.is_past:
        flash('This event has already passed.', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))
    if event.is_sold_out:
        flash('Sorry, this event is sold out!', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))

    if request.method == 'POST':
        tickets = int(request.form.get('tickets', 1))
        attendee_name = request.form.get('attendee_name', current_user.username)
        attendee_email = request.form.get('attendee_email', current_user.email)

        if tickets < 1 or tickets > min(10, event.available_seats):
            flash('Invalid ticket count.', 'danger')
            return redirect(url_for('bookings.book', event_id=event_id))

        existing = Booking.query.filter_by(user_id=current_user.id, event_id=event_id, status='confirmed').first()
        if existing:
            flash('You already have a booking for this event!', 'warning')
            return redirect(url_for('bookings.my_bookings'))

        booking = Booking(
            user_id=current_user.id, event_id=event_id,
            tickets_count=tickets, total_price=tickets * event.price,
            attendee_name=attendee_name, attendee_email=attendee_email
        )
        db.session.add(booking)
        db.session.flush()
        booking.qr_code_path = generate_qr(booking)
        db.session.commit()
        flash('Booking confirmed! Check your tickets below.', 'success')
        return redirect(url_for('bookings.confirmation', booking_id=booking.id))

    max_tickets = min(10, event.available_seats)
    return render_template('bookings/book.html', event=event, max_tickets=max_tickets, title=f'Book - {event.title}')

@bookings.route('/confirmation/<int:booking_id>')
@login_required
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
    return render_template('bookings/confirmation.html', booking=booking, title='Booking Confirmed!')

@bookings.route('/my-bookings')
@login_required
def my_bookings():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('bookings/my_bookings.html', bookings=user_bookings, title='My Tickets')

@bookings.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
    if booking.event.is_past:
        flash('Cannot cancel a past event booking.', 'warning')
        return redirect(url_for('bookings.my_bookings'))
    booking.status = 'cancelled'
    db.session.commit()
    flash('Booking cancelled successfully.', 'info')
    return redirect(url_for('bookings.my_bookings'))
