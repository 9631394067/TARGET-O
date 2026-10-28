from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField, SubmitField, DateField, TimeField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20)])
    event_date = DateField('Event Date', validators=[DataRequired()])
    event_time = TimeField('Event Time', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired(), Length(max=300)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('Music', 'Music'), ('Technology', 'Technology'), ('Sports', 'Sports'),
        ('Art', 'Art & Culture'), ('Food', 'Food & Drinks'), ('Business', 'Business'),
        ('Health', 'Health & Wellness'), ('Education', 'Education'),
        ('Comedy', 'Comedy'), ('General', 'General'),
    ])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1, max=100000)])
    price = FloatField('Ticket Price', validators=[DataRequired(), NumberRange(min=0)])
    banner_image = FileField('Event Banner', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    is_featured = BooleanField('Feature this Event')
    submit = SubmitField('Publish Event')
