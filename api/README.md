# Artemis Backend API

A Django REST Framework backend for the Artemis monitoring system.

## Features

- User management with roles and supervisor assignments
- Biometric data tracking
- Geolocation monitoring
- Alert system
- Event logging
- Recommendations
- Reporting

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements/dev.txt`
5. Copy .env.example to .env and configure
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: `python manage.py runserver`

## API Endpoints

- /api/users/ - User management
- /api/biometrics/ - Biometric data
- /api/geolocation/ - Location data
- /api/alerts/ - Alerts
- /api/events/ - Events
- /api/recommendations/ - Recommendations
- /api/reports/ - Reports

## Database

The project is configured for MySQL. Update settings for your database.

## Testing

Run tests with: `pytest`