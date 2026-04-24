# Container Logistics Management System

Web application for managing container logistics operations.

## Features

- Booking management
- Container tracking
- Role-based access (Agent / Forwarder)
- Payload validation
- Overdue container detection
- Dashboard with analytics
- Damage photo upload

## Tech Stack

- Python
- Django
- SQLite
- Bootstrap 5
- Pillow

## Roles

- **Agent (Admin)** – manages all data
- **Forwarder** – works only with own bookings

## Functionality

- Create and manage bookings
- Track container status and location
- Control cargo weight vs payload
- Detect overdue containers
- Upload damage photos

## Setup

```bash
git clone https://github.com/Ivan353003/logistics_project.git
cd logistics_project

python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
