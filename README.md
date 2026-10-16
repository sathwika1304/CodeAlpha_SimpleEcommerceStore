# CodeAlpha Simple E-commerce Store

A beginner-friendly full-stack e-commerce project built with Django, HTML, CSS, JavaScript-ready templates, and SQLite. This project is intended for local learning and internship demonstration.

## Features
- Responsive storefront and product details
- Django admin product management
- Registration, login, and logout using Django authentication
- Session-based shopping cart with quantity updates/removal
- Checkout form with server-side validation
- Cash on Delivery checkout (no fake online-payment flow)
- Orders and order items saved to the database
- Stock validation and stock reduction when an order is placed
- Logged-in users can view only their own orders

## Requirements
- Python 3.10+
- pip

## Run on Ubuntu/Linux
Open a terminal inside this project folder.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open these addresses in your browser:
- Store: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Sign in to the admin panel using the superuser details you created. Open **Products → Add product** and add a few products with a name, description, price, stock, and optional public image URL. Return to the store homepage to see them.

## First test checklist
1. Add at least two products in Django admin.
2. Open the home page and view product details.
3. Add an item to the cart; update quantity and remove it.
4. Register a normal user account and log in.
5. Add products and place a Cash on Delivery order.
6. Open **My Orders** and inspect the order details.
7. Check the admin panel to confirm the order was saved and stock was reduced.

## GitHub repository name
`CodeAlpha_SimpleEcommerceStore`

## Before public deployment
This is a learning project configured for local development (`DEBUG = True`) with a development-only secret key. Before deploying publicly, use environment variables for the secret key, set `DEBUG = False`, configure production `ALLOWED_HOSTS`, HTTPS/cookie settings, static file serving, backups, and a production database. Do not collect real customer or payment information in a demo deployment.
