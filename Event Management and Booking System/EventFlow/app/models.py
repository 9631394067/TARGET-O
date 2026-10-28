from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='attendee')
    avatar = db.Column(db.String(200), default='default_avatar.png')
    bio = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship('Event', backref='organizer', lazy=True, foreign_keys='Event.organizer_id')
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_organizer(self):
        return self.role in ['organizer', 'admin']

    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='')
    category = db.Column(db.String(50), default='General')
    capacity = db.Column(db.Integer, nullable=False, default=100)
    price = db.Column(db.Float, nullable=False, default=0.0)
    banner_image = db.Column(db.String(300), default='default_event.jpg')
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='event', lazy=True)

    @property
    def booked_count(self):
        return sum(b.tickets_count for b in self.bookings if b.status == 'confirmed')

    @property
    def available_seats(self):
        return self.capacity - self.booked_count

    @property
    def is_sold_out(self):
        return self.available_seats <= 0

    @property
    def is_past(self):
        return self.event_date < datetime.utcnow().date()

    @property
    def revenue(self):
        return sum(b.total_price for b in self.bookings if b.status == 'confirmed')

    def __repr__(self):
        return f'<Event {self.title}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    tickets_count = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default='confirmed')
    booking_ref = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4())[:8].upper())
    qr_code_path = db.Column(db.String(300), default='')
    attendee_name = db.Column(db.String(100), default='')
    attendee_email = db.Column(db.String(120), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.booking_ref}>'
