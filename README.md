# 🛍 VelvetCart — Django E-Commerce

A full-featured e-commerce web application built with Django, featuring product listings, shopping cart, user authentication, and order processing.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Product Catalog** | Grid layout with categories, search, and sort |
| **Product Detail** | Full page with related products, stock indicator |
| **Shopping Cart** | Add/remove/update quantities via AJAX (no page reload) |
| **Checkout** | Delivery info + payment method selection |
| **Order Processing** | Orders saved to DB, stock auto-decremented |
| **Order History** | List and detail view per user |
| **User Registration** | Sign up with username, name, email, password |
| **User Login / Logout** | Session-based auth |
| **User Profile** | Update personal info and address |
| **Admin Panel** | Manage products, orders, categories at `/admin/` |

---

## 🚀 Quick Start

### 1. Clone / navigate into the project
```bash
cd ecommerce
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Apply database migrations
```bash
python manage.py migrate
```

### 4. Seed sample data (products + users)
```bash
python manage.py seed_data
```
This creates:
- **Admin user**: `admin` / `admin123`
- **Demo user**: `demo` / `demo123`
- **5 categories** and **14 sample products**

### 5. Run the development server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## 📁 Project Structure

```
ecommerce/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← created after migrations
├── media/                  ← uploaded product images
│   └── products/
├── ecommerce/              ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── store/                  ← Main application
    ├── models.py           ← Category, Product, Order, OrderItem, UserProfile
    ├── views.py            ← All view functions
    ├── urls.py             ← URL routing
    ├── forms.py            ← Django forms
    ├── admin.py            ← Admin customization
    ├── context_processors.py
    ├── migrations/
    ├── management/
    │   └── commands/
    │       └── seed_data.py
    ├── static/store/
    │   ├── css/style.css   ← All styles
    │   └── js/main.js      ← AJAX cart interactions
    └── templates/store/
        ├── base.html
        ├── product_list.html
        ├── product_detail.html
        ├── cart.html
        ├── checkout.html
        ├── order_confirmation.html
        ├── order_list.html
        ├── order_detail.html
        ├── login.html
        ├── register.html
        └── profile.html
```

---

## 🗄 Database Models

### `Category`
- `name`, `slug`, `description`

### `Product`
- `category` (FK), `name`, `slug`, `description`
- `price`, `stock`, `image`, `available`

### `Order`
- `user` (FK), `status` (pending/processing/shipped/delivered/cancelled)
- Delivery fields: `first_name`, `last_name`, `email`, `address`, `city`, `postal_code`
- `payment_method` (cod/card/upi), `paid`, `notes`

### `OrderItem`
- `order` (FK), `product` (FK), `price`, `quantity`

### `UserProfile`
- `user` (OneToOne), `phone`, `address`, `city`, `postal_code`, `avatar`

---

## 🔗 URL Routes

| URL | View | Description |
|---|---|---|
| `/` | `product_list` | Home / product catalog |
| `/product/<slug>/` | `product_detail` | Product detail page |
| `/cart/` | `cart_detail` | Shopping cart |
| `/cart/add/<id>/` | `cart_add` | Add to cart (POST/AJAX) |
| `/cart/remove/<id>/` | `cart_remove` | Remove from cart |
| `/cart/update/<id>/` | `cart_update` | Update quantity (AJAX) |
| `/checkout/` | `checkout` | Checkout form |
| `/order/<id>/confirmation/` | `order_confirmation` | Success page |
| `/orders/` | `order_list` | User's order history |
| `/order/<id>/` | `order_detail` | Order detail |
| `/register/` | `register` | Sign up |
| `/login/` | `user_login` | Sign in |
| `/logout/` | `user_logout` | Sign out |
| `/profile/` | `profile` | Edit profile |
| `/admin/` | Django Admin | Admin panel |

---

## ⚙️ Configuration

Edit `ecommerce/settings.py` for:
- `SECRET_KEY` — change before production
- `DEBUG = False` — for production
- `ALLOWED_HOSTS` — add your domain
- `DATABASES` — switch to PostgreSQL for production

### Adding product images via Admin
1. Go to `/admin/` → Products → Add Product
2. Fill in details and upload an image
3. The image will appear on the product card and detail page

---

## 🛠 Tech Stack

- **Backend**: Django 4.2 (Python)
- **Database**: SQLite (dev) — easily switch to PostgreSQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Fonts**: Google Fonts (Inter + Playfair Display)
- **Cart**: Session-based with AJAX updates
- **Auth**: Django's built-in auth system

---

## 🔐 Default Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Demo User | `demo` | `demo123` |

> ⚠️ Change these in production!
