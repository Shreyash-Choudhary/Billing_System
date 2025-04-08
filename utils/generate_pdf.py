# utils/generate_pdf.py
from fpdf import FPDF
from datetime import datetime
import os

def create_pdf(cart, total, customer_name, phone_number, discount, tax):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="GoVigyan Billing System", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=2, align="C")
    pdf.cell(200, 10, txt=f"Customer: {customer_name} | Phone: {phone_number}", ln=3, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=10)
    pdf.cell(40, 10, "Product", 1)
    pdf.cell(30, 10, "Category", 1)
    pdf.cell(20, 10, "Qty", 1)
    pdf.cell(30, 10, "Price", 1)
    pdf.cell(30, 10, "Total", 1)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for item in cart:
        pdf.cell(40, 10, item['name'], 1)
        pdf.cell(30, 10, item['category'], 1)
        pdf.cell(20, 10, str(item['quantity']), 1)
        pdf.cell(30, 10, f"{item['price']:.2f}", 1)
        pdf.cell(30, 10, f"{item['total']:.2f}", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.cell(150, 10, "Subtotal:", 0, 0, 'R')
    pdf.cell(30, 10, f"{total:.2f}", 0, 1, 'R')

    pdf.cell(150, 10, "Discount (10%):", 0, 0, 'R')
    pdf.cell(30, 10, f"-{discount:.2f}", 0, 1, 'R')

    pdf.cell(150, 10, "Tax (5%):", 0, 0, 'R')
    pdf.cell(30, 10, f"{tax:.2f}", 0, 1, 'R')

    final_total = total - discount + tax
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, "Final Total:", 0, 0, 'R')
    pdf.cell(30, 10, f"{final_total:.2f}", 0, 1, 'R')

    if not os.path.exists("generated_bills"):
        os.makedirs("generated_bills")

    file_path = f"generated_bills/bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(file_path)

    return file_path

