# Chat-App

## Overview
Chat-App is a real-time messaging platform that allows users to communicate with friends instantly. Users can send text messages, images, and files, making the communication process more dynamic. The app uses WebSockets for real-time messaging and Redis for handling message queues. It also features a friend request system and email verification for added security.

## Features

- **Real-time Communication**: Users can send and receive text messages, images, and files in real-time using WebSockets, powered by Django Channels and Redis.
- **Friend Request System**: Users can send, accept, and manage friend requests, making it easy to connect with others and communicate securely.
- **Email Verification**: Ensures a secure registration process by verifying user email during signup.
- **User Authentication**: Secure login and session management through Django's authentication system.
- **Modern UI**: A responsive and attractive user interface built using TailwindCSS.
- **Media Sharing**: Users can send images and files in chats for a richer communication experience.

## Technologies Used

- **Backend**: Django, Django Channels, Redis
- **Database**: PostgreSQL
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Real-Time Communication**: WebSockets, Redis
- **Authentication**: Django's default authentication system
- **Email Verification**: Integrated email verification system

## Installation

### Prerequisites

- Python (version 3.8 or above)
- PostgreSQL

### Steps to run the project locally:

1. **Clone the repository:**

   ```bash
   https://github.com/saminmahmud/Chat-App.git
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. **Install required Python dependencies:**
   ```bash
   pip install -r requirements.txt
4. **Set up PostgreSQL Database:**
  - Create a new PostgreSQL database and configure the DATABASES setting in settings.py accordingly.
  - Run the migrations:
     ```bash
    python manage.py migrate
5. **Start the Development Server:**
   ```bash
   python manage.py runserver
6. **Open the browser and go to:**
   ```bash
   http://127.0.0.1:8000/

