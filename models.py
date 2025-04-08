# models.py
from datetime import datetime
from extensions import db
from flask_sqlalchemy import SQLAlchemy

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))  # Govigyan or Medicinal
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')


def init_db():
    db.create_all()
    
    # Default admin
    if not Admin.query.filter_by(username='admin').first():
        db.session.add(Admin(username='admin', password='admin123'))

    # Default worker
    if not Worker.query.filter_by(username='worker').first():
        db.session.add(Worker(username='worker', password='worker123'))

    db.session.commit()   



