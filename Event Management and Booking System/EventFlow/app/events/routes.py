import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import Event, Booking
from app.events.forms import EventForm
from werkzeug.utils import secure_filename

events = Blueprint('events', __name__)

CATEGORY_ICONS = {
    'Music': '🎵', 'Technology': '💻', 'Sports': '⚽', 'Art': '🎨',
    'Food': '🍕', 'Business': '💼', 'Health': '🏃', 'Education': '📚',
    'Comedy': '😂', 'General': '🎪'
}

def save_image(file):
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return filename
    return None

@events.route('/')
def list_events():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'date')

    query = Event.query.filter_by(is_active=True)
    if search:
        query = query.filter(Event.title.ilike(f'%{search}%') | Event.city.ilike(f'%{search}%') | Event.description.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    if sort == 'price':
        query = query.order_by(Event.price.asc())
    elif sort == 'popular':
        query = query.order_by(Event.id.desc())
    else:
        query = query.order_by(Event.event_date.asc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    categories = ['Music', 'Technology', 'Sports', 'Art', 'Food', 'Business', 'Health', 'Education', 'Comedy', 'General']
    return render_template('events/list.html', events=pagination.items, pagination=pagination,
                           categories=categories, category_icons=CATEGORY_ICONS,
                           search=search, selected_category=category, sort=sort, title='All Events')

@events.route('/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    related = Event.query.filter(Event.category == event.category, Event.id != event_id, Event.is_active == True).limit(3).all()
    user_booked = False
    if current_user.is_authenticated:
        user_booked = Booking.query.filter_by(user_id=current_user.id, event_id=event_id, status='confirmed').first()
    return render_template('events/detail.html', event=event, related=related,
                           category_icons=CATEGORY_ICONS, user_booked=user_booked, title=event.title)

@events.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_organizer():
        flash('Only organizers can create events.', 'danger')
        return redirect(url_for('main.index'))
    form = EventForm()
    if form.validate_on_submit():
        banner = save_image(form.banner_image.data)
        event = Event(
            title=form.title.data, description=form.description.data,
            event_date=form.event_date.data, event_time=form.event_time.data,
            venue=form.venue.data, city=form.city.data, category=form.category.data,
            capacity=form.capacity.data, price=form.price.data,
            banner_image=banner or 'default_event.jpg',
            organizer_id=current_user.id, is_featured=form.is_featured.data
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    return render_template('events/create.html', form=form, title='Create Event')

@events.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id and not current_user.is_admin():
        abort(403)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        banner = save_image(form.banner_image.data)
        event.title = form.title.data
        event.description = form.description.data
        event.event_date = form.event_date.data
        event.event_time = form.event_time.data
        event.venue = form.venue.data
        event.city = form.city.data
        event.category = form.category.data
        event.capacity = form.capacity.data
        event.price = form.price.data
        event.is_featured = form.is_featured.data
        if banner:
            event.banner_image = banner
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    return render_template('events/create.html', form=form, event=event, title='Edit Event')

@events.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id and not current_user.is_admin():
        abort(403)
    event.is_active = False
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('events.list_events'))
