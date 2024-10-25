# Cleaning Website

A web application designed for managing and approving cleaning assessments in real-time, tailored for environments like shopping centers and other facilities. This app allows administrators and staff to input, review, and approve cleaning and maintenance marks, ensuring synchronized updates across all user sessions for efficient, up-to-date facility management.

## Features

- **Real-Time Updates**: Users can submit and approve marks in real-time, with immediate synchronization across all active sessions.
- **Data Persistence**: Approved changes are saved to the database, ensuring consistency across user sessions.
- **User Management**: Includes functionality for user registration, login, and management.
- **Admin Panel**: An admin interface for managing users, reviewing data, and controlling application settings.
- **Configurable Objects**: Allows creation and customization of new objects via a configurator interface.
- **Dockerized Environment**: Dockerized setup for development and production simplifies deployment and maintenance.
- **Secure & Scalable**: Configured with Nginx and Certbot SSL to run on an Ubuntu LTS server for a secure, production-grade setup.

## Technologies Used

### Backend
- **Django**: High-level Python web framework for backend logic and database management.
- **Django Channels**: Extends Django to handle asynchronous communications, enabling WebSocket support for real-time interactions.
- **Redis**: Message broker for real-time data exchange and WebSocket connections.
- **PostgreSQL**: A relational database management system for reliable and efficient data storage.

### Frontend
- **TypeScript and JavaScript**: Enables interactive client-side functionality for real-time updates.
- **HTML & CSS**: Fundamental technologies for structuring and styling the application.

### Infrastructure
- **CI/CD Pipeline**: Automated deployment pipeline using GitHub Actions, enabling continuous integration and delivery with automated testing, building, and deployment processes across development and production environments.
- **Docker**: Containerization for consistent environment configuration across development and production.
- **Docker Compose**: Manages multi-container applications, enabling services for Django, PostgreSQL, Redis, Nginx, and Certbot.
- **Nginx**: Serves as a reverse proxy, ensuring load balancing and SSL termination for secure connections.
- **Certbot**: Automates SSL certificate generation and renewal for HTTPS.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/akim-13/cleaning-website.git
   cd cleaning-website
   ```

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
