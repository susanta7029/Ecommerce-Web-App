# Ecommerce Web App

A modern, full-featured Django-based ecommerce platform with Stripe payments, wishlist, reviews, order management, and admin controls.

## Features
- User registration, login, and profile management
- Product listing, detail, and search
- Wishlist functionality
- Product reviews and ratings
- Shopping cart and order management
- Stripe payment integration (secure, using environment variables)
- Admin/staff product and order management
- Responsive, modern UI/UX
- Secure secret management (no secrets in code or git history)

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone https://github.com/susanta7029/Ecommerce-Web-App.git
   cd Ecommerce-Web-App
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv env
   env\Scripts\activate  # On Windows
   # or
   source env/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   *(If `requirements.txt` is missing, install manually: `pip install django python-dotenv stripe pillow`)*

4. **Create a `.env` file in the project root:**
   ```env
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   ```

5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

6. **Create a superuser (admin):**
   ```sh
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

8. **Access the app:**
   - Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Deployment
- Ensure `.env` and other sensitive files are not committed (see `.gitignore`).
- For production, set `DEBUG = False` and configure `ALLOWED_HOSTS` in `settings.py`.
- Use a production-ready database and static/media file hosting.

## Security
- Stripe keys and other secrets are loaded from `.env` (never hardcoded).
- Git history has been cleaned of all secrets.

## License
This project is for portfolio and educational use. Contact the author for commercial licensing.

---

**Author:** susanta7029
