from flask import Blueprint, render_template
from app.models import Event, Booking, User
from app import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    featured_events = Event.query.filter_by(is_featured=True, is_active=True).order_by(Event.event_date.asc()).limit(6).all()
    upcoming_events = Event.query.filter(
        Event.is_active == True,
        Event.event_date >= datetime.utcnow().date()
    ).order_by(Event.event_date.asc()).limit(8).all()

    categories = [
        {'name': 'Music', 'icon': '🎵', 'color': '#7c3aed'},
        {'name': 'Technology', 'icon': '💻', 'color': '#06b6d4'},
        {'name': 'Sports', 'icon': '⚽', 'color': '#10b981'},
        {'name': 'Art', 'icon': '🎨', 'color': '#f59e0b'},
        {'name': 'Food', 'icon': '🍕', 'color': '#ef4444'},
        {'name': 'Business', 'icon': '💼', 'color': '#8b5cf6'},
        {'name': 'Health', 'icon': '🏃', 'color': '#14b8a6'},
        {'name': 'Education', 'icon': '📚', 'color': '#3b82f6'},
    ]

    stats = {
        'events': Event.query.filter_by(is_active=True).count(),
        'users': User.query.count(),
        'bookings': Booking.query.filter_by(status='confirmed').count(),
        'cities': db.session.query(Event.city).distinct().count(),
    }

    return render_template('index.html', featured_events=featured_events,
                           upcoming_events=upcoming_events, categories=categories,
                           stats=stats, title='EventFlow - Discover Amazing Events')

@main.route('/about')
def about():
    return render_template('about.html', title='About EventFlow')

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@main.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
