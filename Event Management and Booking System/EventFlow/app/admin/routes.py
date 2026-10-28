from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Event, Booking
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_events = Event.query.filter_by(is_active=True).count()
    total_bookings = Booking.query.filter_by(status='confirmed').count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter_by(status='confirmed').scalar() or 0
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    top_events = Event.query.filter_by(is_active=True).all()
    top_events.sort(key=lambda e: e.booked_count, reverse=True)
    top_events = top_events[:5]

    category_stats = {}
    for event in Event.query.filter_by(is_active=True).all():
        cat = event.category
        if cat not in category_stats:
            category_stats[cat] = {'count': 0, 'bookings': 0}
        category_stats[cat]['count'] += 1
        category_stats[cat]['bookings'] += event.booked_count

    return render_template('admin/dashboard.html',
                           total_users=total_users, total_events=total_events,
                           total_bookings=total_bookings, total_revenue=total_revenue,
                           recent_bookings=recent_bookings, top_events=top_events,
                           category_stats=category_stats, title='Admin Dashboard')

@admin.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users, title='Manage Users')

@admin.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't deactivate yourself!", 'danger')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'suspended'
    flash(f'User {user.username} has been {status}.', 'info')
    return redirect(url_for('admin.users'))

@admin.route('/users/<int:user_id>/promote', methods=['POST'])
@login_required
@admin_required
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = ['attendee', 'organizer', 'admin']
    current_idx = roles.index(user.role)
    user.role = roles[min(current_idx + 1, 2)]
    db.session.commit()
    flash(f'{user.username} promoted to {user.role}.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/events')
@login_required
@admin_required
def events():
    all_events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/events.html', events=all_events, title='Manage Events')

@admin.route('/bookings')
@login_required
@admin_required
def all_bookings():
    page = request.args.get('page', 1, type=int)
    all_b = Booking.query.order_by(Booking.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/bookings.html', bookings=all_b, title='All Bookings')
