from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response, flash
from flask_babel import Babel, gettext as _ # etc.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from forms import ProductForm
from flask import flash
import os



app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'your_secret_key'
app.config['SECRET_KEY'] = 'your-secret-key-here'


# Database config
basedir = os.path.abspath(os.path.dirname(__file__))  # 👈 ensures you're in your current project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'govigyan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Multilingual config
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

# -------------------- Models --------------------
class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# models.py or in your Product model in app.py (SQLAlchemy)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    customer_name = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)  # ✅ This is correct
    quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


# -------------------- Language Settings --------------------
@babel.localeselector
def get_locale():
    return request.cookies.get('language') or 'en'

@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

@app.route('/set_language/<lang>')
def set_language(lang):
    response = make_response(redirect(request.referrer or url_for('home')))
    response.set_cookie('language', lang)
    return response



# -------------------- Auth --------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        worker = Worker.query.filter_by(username=username, password=password).first()

        if worker:
            session['worker'] = worker.username
            flash("Login successful!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('worker', None)
    return redirect(url_for('login'))

# -------------------- Home --------------------
@app.route('/home')
def home():
    if 'worker' not in session:
        return redirect(url_for('login'))

    products = Product.query.filter_by(is_active=True).all()


    # Prepare chart data even if it's empty
    chart_labels = []
    chart_data = []

    return render_template(
        'home.html',
        products=products,
        chart_labels=chart_labels,
        chart_data=chart_data
    )




# -------------------- Add Product --------------------
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'worker' not in session:
        return redirect(url_for('login'))

    form = ProductForm()

    if form.validate_on_submit():
        new_product = Product(
    name=form.name.data,
    price=form.price.data,
    quantity=form.quantity.data,
    is_active=False  # mark as inactive initially
)

        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for('home'))  # ✅ Redirect to home after adding
    else:
        if request.method == 'POST':
            flash("Please correct the errors in the form.", "danger")

    products = Product.query.all()
    return render_template('add_product.html', form=form, products=products)



# -------------------- Billing --------------------
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if 'worker' not in session:
        return redirect(url_for('login'))

    products = Product.query.filter_by(is_active=True).all()
    cart = session.get('cart', [])
    grand_total = sum(item['total'] for item in cart)

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        phone_number = request.form['phone_number']
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])

        product = Product.query.get(product_id)
        if product and product.quantity >= quantity:
            product.quantity -= quantity
            total_price = quantity * product.price

            # Add to session cart
            for item in cart:
                if item['id'] == product.id:
                    item['quantity'] += quantity
                    item['total'] = item['quantity'] * product.price
                    break
            else:
                cart.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': quantity,
                    'total': total_price
                })

            # Add to DB Sales
            sale = Sale(
                product_id=product.id,
                quantity=quantity,
                total_price=total_price,
                customer_name=customer_name,
                phone_number=phone_number
            )
            db.session.add(sale)
            db.session.commit()

            session['cart'] = cart
            session['customer_name'] = customer_name
            session['phone_number'] = phone_number
            flash(_('Product added to bill.'), 'success')
        else:
            flash(_('Insufficient stock or product not found.'), 'danger')

        return redirect(url_for('billing'))

    return render_template(
        'billing.html',
        products=products,
        cart=cart,
        grand_total=grand_total,
        customer_name=session.get('customer_name', ''),
        phone_number=session.get('phone_number', '')
    )

# -------------------- Reset Cart --------------------
@app.route('/reset_cart', methods=['POST'])
def reset_cart():
    session.pop('cart', None)
    session.pop('customer_name', None)
    session.pop('phone_number', None)
    flash(_('Bill cleared.'), 'info')
    return redirect(url_for('billing'))

# -------------------- Generate PDF Bill --------------------
@app.route('/generate_pdf_bill', methods=['GET', 'POST'])
def generate_pdf_bill():
    cart = session.get('cart', [])
    customer_name = session.get('customer_name', 'Customer')
    phone_number = session.get('phone_number', 'N/A')

    subtotal = sum(item['total'] for item in cart)
    gst = round(subtotal * 0.18, 2)
    grand_total = round(subtotal + gst, 2)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, 770, "GoVigyan Billing System")

    p.setFont("Helvetica", 12)
    p.drawString(50, 740, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    p.drawString(50, 725, f"Customer Name: {customer_name}")
    p.drawString(50, 710, f"Phone: {phone_number}")

    # Table
    y = 680
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Product")
    p.drawString(200, y, "Price")
    p.drawString(300, y, "Qty")
    p.drawString(370, y, "Total")
    y -= 20

    p.setFont("Helvetica", 10)
    for item in cart:
        p.drawString(50, y, item['name'])
        p.drawString(200, y, f"{item['price']}")
        p.drawString(300, y, f"{item['quantity']}")
        p.drawString(370, y, f"{item['total']}")
        y -= 20
        if y < 100:
            p.showPage()
            y = 750

    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y - 20, f"Subtotal: ₹{subtotal}")
    p.drawString(300, y - 40, f"GST (18%): ₹{gst}")
    p.drawString(300, y - 60, f"Grand Total: ₹{grand_total}")
    p.setFont("Helvetica", 10)
    p.drawString(50, 50, "Thank you for shopping with GoVigyan!")

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='invoice.pdf', mimetype='application/pdf')

# -------------------- Dashboard --------------------
@app.route('/dashboard')
def dashboard():
    if 'worker' not in session:
        return redirect(url_for('login'))

    total_products = Product.query.count()
    low_stock_count = Product.query.filter(Product.quantity < 10).count()
    low_stock_items = Product.query.filter(Product.quantity < 10).all()
    total_sales = db.session.query(db.func.sum(Sale.total_price)).scalar() or 0

    recent_sales = db.session.query(
        db.func.date(Sale.timestamp).label('date'),
        db.func.sum(Sale.total_price).label('daily_total')
    ).group_by('date').order_by('date').limit(7).all()

    sales_labels = [datetime.strptime(row.date, "%Y-%m-%d").strftime("%d %b") for row in recent_sales]
    sales_data = [float(row.daily_total) for row in recent_sales]

    # 🔔 NEW: Get low stock items list
    low_stock_items = Product.query.filter(Product.stock < 10).all()

    return render_template('dashboard.html',
                           total_products=total_products,
                           low_stock_count=low_stock_count,
                           total_sales=total_sales,
                           sales_labels=sales_labels,
                           sales_data=sales_data,
                           low_stock_items=low_stock_items)  # 👈 Pass this



# -------------------- Report --------------------
@app.route('/report')
def report():
    if 'worker' not in session:
        return redirect(url_for('login'))

    sales = Sale.query.all()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    y = 800
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, "GoVigyan Sales Report")
    y -= 30
    p.setFont("Helvetica", 11)

    for sale in sales:
        product = Product.query.get(sale.product_id)
        line = f"{sale.timestamp.strftime('%Y-%m-%d')} - {product.name} x{sale.quantity} - ₹{sale.total_price} - {sale.customer_name} ({sale.phone_number})"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype='application/pdf')

# -------------------- Run --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Worker.query.filter_by(username='admin').first():
            db.session.add(Worker(username='admin', password='admin123'))
            db.session.commit()
    app.run(debug=True)    
