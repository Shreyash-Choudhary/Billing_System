# Smart Billing System

Smart Billing System is a comprehensive billing management application developed using Flask. It enables businesses to manage products, process sales, generate invoices, and produce sales reports efficiently.

## Features

- **User Authentication**: Secure login and logout functionalities for workers.
- **Product Management**: Add, update, and monitor product details including stock levels.
- **Billing**: Create invoices for customers, calculate totals with GST, and generate PDF bills.
- **Sales Reporting**: Generate and download sales reports in PDF format.
- **Dashboard**: View key metrics such as total products, low stock alerts, and recent sales trends.
- **Multi-language Support**: Set and change the application language preference.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/smart-billing-system.git
   ```


2. **Navigate to the Project Directory**:

   ```bash
   cd smart-billing-system
   ```


3. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   ```


4. **Activate the Virtual Environment**:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

5. **Install Required Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```


6. **Set Up the Database**:

   ```bash
   flask db upgrade
   ```


   *This will create the necessary database tables.*

7. **Run the Application**:

   ```bash
   flask run
   ```


   *The application will be accessible at `http://127.0.0.1:5000/`.*

## Usage

- **Login**: Access the system using worker credentials.
- **Dashboard**: View an overview of products, sales, and alerts.
- **Product Management**: Navigate to the product section to add or update product details.
- **Billing**: Process customer purchases and generate invoices.
- **Reports**: Generate and download sales reports as needed.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Flask Framework](https://flask.palletsprojects.com/)
- [ReportLab for PDF Generation](https://www.reportlab.com/)
- [Bootstrap for Frontend Components](https://getbootstrap.com/)

*For a similar project and inspiration, refer to [Billing-Flask](https://github.com/SudeepAcharjee/Billing-Flask).* 