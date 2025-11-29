# alx_travel_app_0x01

Django backend for a travel booking platform with **Listings**, **Bookings**, and **Reviews**. Provides RESTful APIs via **Django REST Framework (DRF)** and includes a **database seeder** to populate sample data.  

This service handles core booking logic and user interactions (hosts and guests) and can be extended to integrate into a **microservices architecture** in the future, using tools like **RabbitMQ** for inter-service communication.  

## Features

- Manage Listings, Bookings, and Reviews via API  
- Nested user information for hosts and guests  
- Role-based validations (guests vs hosts)  
- Public endpoints for browsing listings and reviews  
- API authentication using session or token-based login  
- Seeder to populate the database with sample data  

## Next Steps / Work in Progress

- Integration with **other microservices** for payments, notifications, authenticaion and messaging  
- Event-driven communication using **RabbitMQ**  
- Enhanced permissions and filtering for bookings and reviews  
- Token-based authentication for production-ready API  

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed  # populate sample data
python manage.py runserver
```

## API Endpoints

- `/api/listings/` - list, retrieve, create, update, delete listings
- `/api/listings/<listing_id>/reviews/` - list, retrieve, create, update, delete reviews
- `/api/bookings/` - list, retrieve, create, update, delete bookings
- `/api/bookings/?listing=<listing_id>/` - list all bookings for a specific listing
- `/swagger/` - interactive API documentation