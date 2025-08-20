#!/bin/bash

echo "Setting up 77.uz Marketplace project..."

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate

# Create translations
python manage.py makemessages -l uz
python manage.py makemessages -l ru
python manage.py compilemessages

# Create admin user and sample data
python manage.py setup_admin

# Collect static files
python manage.py collectstatic --noinput

echo "Setup completed successfully!"
echo ""
echo "Admin credentials:"
echo "Phone: +998901234567"
echo "Password: admin123"
echo ""
echo "To start the server:"
echo "python manage.py runserver"
echo ""
echo "Admin panel: http://localhost:8000/admin/"
echo "API docs: http://localhost:8000/api/docs/"
