"""
EventFlow - Sample Data Seeder
Run: python seed.py
"""
from app import create_app, db
from app.models import User, Event, Booking
from datetime import datetime, date, time, timedelta
import random, uuid

app = create_app()

def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("🗃️  Database reset...")

        # ===== USERS =====
        admin = User(username='admin', email='admin@eventflow.com', role='admin')
        admin.set_password('admin123')

        org1 = User(username='rahul_events', email='organizer@eventflow.com', role='organizer', bio='Top event organizer in Mumbai')
        org1.set_password('org123')

        org2 = User(username='priya_shows', email='priya@eventflow.com', role='organizer', bio='Music & Art event specialist')
        org2.set_password('org123')

        org3 = User(username='tech_guru', email='tech@eventflow.com', role='organizer', bio='Tech conferences and workshops')
        org3.set_password('org123')

        user1 = User(username='ankit', email='user@eventflow.com', role='attendee')
        user1.set_password('user123')

        user2 = User(username='sneha', email='sneha@eventflow.com', role='attendee')
        user2.set_password('user123')

        user3 = User(username='vikram', email='vikram@eventflow.com', role='attendee')
        user3.set_password('user123')

        user4 = User(username='meera', email='meera@eventflow.com', role='attendee')
        user4.set_password('user123')

        user5 = User(username='arjun', email='arjun@eventflow.com', role='attendee')
        user5.set_password('user123')

        users = [admin, org1, org2, org3, user1, user2, user3, user4, user5]
        db.session.add_all(users)
        db.session.flush()
        print(f"✅ {len(users)} users created")

        # ===== EVENTS =====
        today = date.today()
        events_data = [
            {
                'title': 'AI & Future Tech Summit 2024',
                'description': 'Join 500+ tech enthusiasts for a day of AI, ML, and future technology talks. Featuring keynotes from Google, Microsoft, and top Indian startups.\n\nTopics include:\n• Large Language Models & Generative AI\n• Computer Vision in Healthcare\n• Edge Computing & IoT\n• Career in AI - Panel Discussion\n\nIncludes lunch, networking session, and certificate of attendance.',
                'event_date': today + timedelta(days=15),
                'event_time': time(10, 0),
                'venue': 'NSCI Dome, Worli',
                'city': 'Mumbai',
                'category': 'Technology',
                'capacity': 500,
                'price': 999,
                'organizer_id': org3.id,
                'is_featured': True,
            },
            {
                'title': 'Arijit Singh Live in Concert',
                'description': 'Experience the magic of Arijit Singh live! An unforgettable evening of soulful melodies and chart-topping hits.\n\nThe concert features:\n• 3-hour live performance\n• Full band setup with 20+ musicians\n• Special acoustic session\n• Pyrotechnics and light show\n\nGates open 2 hours before the show. Food and beverages available at the venue.',
                'event_date': today + timedelta(days=20),
                'event_time': time(18, 30),
                'venue': 'JLN Stadium',
                'city': 'Delhi',
                'category': 'Music',
                'capacity': 5000,
                'price': 2499,
                'organizer_id': org2.id,
                'is_featured': True,
            },
            {
                'title': 'IPL Fan Fest & Cricket Carnival',
                'description': 'The ultimate cricket fan experience! Watch IPL matches on a giant screen with thousands of fellow cricket lovers.\n\n• Live match screening on 40ft LED screen\n• Meet former cricketers\n• Cricket games and competitions\n• Food court with 20+ stalls\n• DJ night after the match',
                'event_date': today + timedelta(days=10),
                'event_time': time(16, 0),
                'venue': 'Phoenix Marketcity',
                'city': 'Bangalore',
                'category': 'Sports',
                'capacity': 2000,
                'price': 499,
                'organizer_id': org1.id,
                'is_featured': True,
            },
            {
                'title': 'Modern Art Exhibition - Colors of India',
                'description': 'A curated exhibition showcasing 100+ artworks by 30 emerging Indian artists. From traditional to contemporary, explore the rich tapestry of Indian art.\n\nFeaturing:\n• Oil paintings, watercolors, digital art\n• Live art demonstrations\n• Art workshops for beginners\n• Meet the artists session',
                'event_date': today + timedelta(days=7),
                'event_time': time(11, 0),
                'venue': 'National Gallery of Modern Art',
                'city': 'Mumbai',
                'category': 'Art',
                'capacity': 300,
                'price': 200,
                'organizer_id': org2.id,
                'is_featured': True,
            },
            {
                'title': 'Street Food Festival - Taste of India',
                'description': 'Sample the best street food from every corner of India under one roof! 50+ food stalls, live cooking demos, and eating competitions.\n\n• Chaat from Delhi, Vada Pav from Mumbai\n• Dosa from Bangalore, Puchka from Kolkata\n• Live cooking by celebrity chefs\n• Kids zone and entertainment',
                'event_date': today + timedelta(days=5),
                'event_time': time(12, 0),
                'venue': 'Jawaharlal Nehru Stadium Ground',
                'city': 'Delhi',
                'category': 'Food',
                'capacity': 3000,
                'price': 299,
                'organizer_id': org1.id,
                'is_featured': True,
            },
            {
                'title': 'Startup India Conclave 2024',
                'description': 'Connect with 200+ startups, investors, and industry leaders. Pitch competitions, funding sessions, and networking opportunities.\n\n• Pitch your startup to top VCs\n• Mentorship sessions\n• Startup showcase exhibition\n• Networking dinner',
                'event_date': today + timedelta(days=25),
                'event_time': time(9, 0),
                'venue': 'ITC Grand Chola',
                'city': 'Chennai',
                'category': 'Business',
                'capacity': 800,
                'price': 1499,
                'organizer_id': org3.id,
                'is_featured': False,
            },
            {
                'title': 'Yoga & Wellness Retreat Weekend',
                'description': 'Rejuvenate your mind, body, and soul with our 2-day wellness retreat. Expert yoga instructors, meditation sessions, and organic meals.\n\n• Morning yoga (6 AM - 8 AM)\n• Meditation & breathwork\n• Organic meals included\n• Nature walks and detox therapy',
                'event_date': today + timedelta(days=12),
                'event_time': time(6, 0),
                'venue': 'Rishikesh Yoga Ashram',
                'city': 'Rishikesh',
                'category': 'Health',
                'capacity': 100,
                'price': 3999,
                'organizer_id': org1.id,
                'is_featured': False,
            },
            {
                'title': 'Python & Django Bootcamp',
                'description': 'Intensive 1-day bootcamp covering Python fundamentals and Django web development. Build a full project by end of day!\n\n• Python basics to advanced\n• Django models, views, templates\n• REST API development\n• Deployment to cloud\n• Certificate included',
                'event_date': today + timedelta(days=18),
                'event_time': time(9, 30),
                'venue': 'WeWork Galaxy, Residency Road',
                'city': 'Bangalore',
                'category': 'Education',
                'capacity': 60,
                'price': 799,
                'organizer_id': org3.id,
                'is_featured': False,
            },
            {
                'title': 'Stand-Up Comedy Night ft. Top Comics',
                'description': 'Get ready for an evening of non-stop laughter! Featuring 5 of India\'s top stand-up comedians.\n\n• 3 hours of comedy\n• Open mic segment\n• Meet & greet after show\n• Drinks available at venue',
                'event_date': today + timedelta(days=8),
                'event_time': time(19, 30),
                'venue': 'Canvas Laugh Club',
                'city': 'Mumbai',
                'category': 'Comedy',
                'capacity': 200,
                'price': 599,
                'organizer_id': org2.id,
                'is_featured': False,
            },
            {
                'title': 'Bollywood Retro Night - 90s Special',
                'description': 'Dance the night away with the best of 90s Bollywood! Live band, DJ, and themed decor.\n\n• Live performance of 90s hits\n• Best dressed contest\n• Themed photo booth\n• Free welcome drink',
                'event_date': today + timedelta(days=14),
                'event_time': time(20, 0),
                'venue': 'The Lalit',
                'city': 'Delhi',
                'category': 'Music',
                'capacity': 400,
                'price': 1299,
                'organizer_id': org2.id,
                'is_featured': False,
            },
            {
                'title': 'Free Community Coding Meetup',
                'description': 'Monthly coding meetup open to all! Share projects, learn new technologies, and network with fellow developers.\n\n• Lightning talks\n• Code reviews\n• Pair programming\n• Free pizza and drinks',
                'event_date': today + timedelta(days=3),
                'event_time': time(18, 0),
                'venue': '91springboard, MG Road',
                'city': 'Bangalore',
                'category': 'Technology',
                'capacity': 80,
                'price': 0,
                'organizer_id': org3.id,
                'is_featured': False,
            },
            {
                'title': 'Marathon - Run for Education',
                'description': 'A 10K charity marathon supporting education for underprivileged children.\n\n• 5K and 10K categories\n• Medal and T-shirt for all finishers\n• Post-run breakfast\n• All proceeds go to charity',
                'event_date': today + timedelta(days=30),
                'event_time': time(5, 30),
                'venue': 'Marine Drive',
                'city': 'Mumbai',
                'category': 'Sports',
                'capacity': 1500,
                'price': 500,
                'organizer_id': org1.id,
                'is_featured': True,
            },
            {
                'title': 'Photography Masterclass',
                'description': 'Learn photography from award-winning photographers. Covers landscape, portrait, street, and mobile photography.\n\n• DSLR and mobile phone techniques\n• Post-processing in Lightroom\n• Outdoor photo walk\n• Portfolio review',
                'event_date': today + timedelta(days=22),
                'event_time': time(10, 0),
                'venue': 'India Habitat Centre',
                'city': 'Delhi',
                'category': 'Education',
                'capacity': 40,
                'price': 1999,
                'organizer_id': org2.id,
                'is_featured': False,
            },
            {
                'title': 'Diwali Night Market',
                'description': 'Celebrate Diwali at our grand night market! Handcrafted gifts, traditional sweets, live performances, and fireworks.\n\n• 100+ handcraft stalls\n• Traditional food court\n• Rangoli making competition\n• Fireworks display at midnight',
                'event_date': today + timedelta(days=35),
                'event_time': time(17, 0),
                'venue': 'Palace Grounds',
                'city': 'Bangalore',
                'category': 'General',
                'capacity': 5000,
                'price': 149,
                'organizer_id': org1.id,
                'is_featured': False,
            },
            {
                'title': 'Data Science Workshop - Hands On',
                'description': 'A practical workshop on data science with Python. Bring your laptop and learn by doing!\n\n• Pandas, NumPy, Matplotlib\n• Machine Learning with scikit-learn\n• Real-world dataset projects\n• Take-home assignments',
                'event_date': today + timedelta(days=28),
                'event_time': time(10, 0),
                'venue': 'T-Hub, IIIT Campus',
                'city': 'Hyderabad',
                'category': 'Technology',
                'capacity': 50,
                'price': 699,
                'organizer_id': org3.id,
                'is_featured': False,
            },
        ]

        event_objs = []
        for data in events_data:
            e = Event(**data)
            db.session.add(e)
            event_objs.append(e)
        db.session.flush()
        print(f"✅ {len(event_objs)} events created")

        # ===== BOOKINGS =====
        attendees = [user1, user2, user3, user4, user5]
        booking_count = 0
        for event_obj in event_objs:
            num_bookings = random.randint(2, min(5, len(attendees)))
            chosen = random.sample(attendees, num_bookings)
            for user in chosen:
                tickets = random.randint(1, 3)
                ref = str(uuid.uuid4())[:8].upper()
                b = Booking(
                    user_id=user.id,
                    event_id=event_obj.id,
                    tickets_count=tickets,
                    total_price=tickets * event_obj.price,
                    attendee_name=user.username,
                    attendee_email=user.email,
                    booking_ref=ref,
                    status='confirmed'
                )
                db.session.add(b)
                booking_count += 1

        db.session.commit()
        print(f"✅ {booking_count} bookings created")
        print("\n" + "="*50)
        print("⚡ EventFlow Database Seeded Successfully!")
        print("="*50)
        print("\n🔑 Login Credentials:")
        print("   Admin:     admin@eventflow.com / admin123")
        print("   Organizer: organizer@eventflow.com / org123")
        print("   Attendee:  user@eventflow.com / user123")
        print("\n🚀 Run: python run.py")
        print("🌐 Open: http://127.0.0.1:5000\n")

if __name__ == '__main__':
    seed()
