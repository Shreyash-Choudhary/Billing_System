from app import db, Worker

# Replace these with desired credentials
username = 'admin'
password = 'admin123'

# Check if user already exists
existing_user = Worker.query.filter_by(username=username).first()
if existing_user:
    print('User already exists!')
else:
    new_user = Worker(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    print('Worker added successfully!')
