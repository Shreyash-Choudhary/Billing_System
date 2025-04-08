from app import app, db
from models import Worker

with app.app_context():
    db.create_all()  # Ensure tables exist

    # Create a worker
    new_worker = Worker(username='worker1', password='1234')  # Change if needed
    db.session.add(new_worker)
    db.session.commit()
    print("✅ Worker created: worker1 / 1234")
