# 🛒 77-UZ Marketplace

Modern Django-based **Marketplace Platform** built with **Django 5**, **Django REST Framework (DRF)**, and **drf_yasg (Swagger UI)** for API documentation.  

## 🚀 Features
- ✅ Custom **User model** with multiple roles (Super Admin, Admin, Seller, Buyer)
- ✅ **Authentication system** (Login, Logout, JWT-ready structure)
- ✅ **Accounts app** with extended User profiles
- ✅ **Common Address model** with relation to Users
- ✅ **Django Admin panel customization**
- ✅ **Swagger API Docs** (`drf_yasg`)
- ✅ Database migrations support

---

## 📂 Project Structure
```
77-uz/
│── apps/
│   ├── accounts/       # Custom User model & auth logic
│   ├── common/         # Shared models (Address, etc.)
│── config/             # Main Django settings & urls
│── manage.py           # Django CLI
│── requirements.txt    # Dependencies
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone repository
```bash
git clone https://github.com/dxrkn1ght/77-uz.git
cd 77-uz
```

### 2️⃣ Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux & Mac
.venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Create superuser
```bash
python manage.py createsuperuser
```

### 6️⃣ Run server
```bash
python manage.py runserver
```

---

## 📖 API Documentation
Swagger UI is available at:  
👉 [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)  

ReDoc alternative:  
👉 [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---

## 🛠 Tech Stack
- **Backend:** Django 5, Django REST Framework
- **Database:** PostgreSQL / SQLite (dev)
- **Docs:** drf_yasg (Swagger & Redoc)
- **Auth:** Custom User + Roles

---

## 📌 Notes
- Make sure `accounts.User` is set as the default user model in `settings.py`:
  ```python
  AUTH_USER_MODEL = "accounts.User"
  ```
- If you face migration conflicts, reset them:
  ```bash
  python manage.py migrate --fake accounts zero
  python manage.py makemigrations
  python manage.py migrate
  ```

---

## 👨‍💻 Author
**Komronbek Zubaydullayev**  
    **dxrkn1ght** 
💼 Backend Developer | Django & DRF | REST APIs  


## Upgrade Notes
- Migrated to drf-spectacular with Swagger and ReDoc at /swagger/ and /redoc/.
- Added CORS and CSRF settings via environment.
- Strengthened permissions and admin performance.
- Fixed pytest configuration and enforced 80% coverage.
- Added Flake8 config.
