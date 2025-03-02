# MovieWeb App

## Overview
MovieWeb App is a simple Flask-based web application that allows users to manage their favorite movies. It provides functionalities for adding users, associating movies with users, updating movie details, and handling errors gracefully. The application uses Flask as the backend framework and SQLAlchemy for database management. Additionally, it integrates with the OMDB API to fetch movie details automatically.

## Features
- List users
- Add new users
- Add movies to a user's favorite list
- Fetch movie details using the OMDB API
- Update movie details
- Delete movies
- Handle errors with a user-friendly interface

## Technologies Used
- **Flask** (Web framework)
- **SQLAlchemy** (Database ORM)
- **OMDB API** (Fetch movie details)
- **Jinja2** (Templating engine)
- **HTML/CSS** (Frontend styling with shared styles across templates)

## Installation
### Prerequisites
- Python 3.8+
- Flask and SQLAlchemy installed
- OMDB API key

### Steps
1. Clone this repository:
   ```sh
   git clone https://github.com/your-username/movieweb-app.git
   cd movieweb-app
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up your OMDB API key:

Create a .env file and insert OMDB_API_KEY = <your-api-key>

5. Run the Flask application:
   ```sh
   python3 app.py
   ```
6. Open your browser and go to `http://127.0.0.1:5000`


## Routes
- `/` → Home page
- `/users` → List all users
- `/add_user` → Add a new user
- `/users/<user_id>/movies` → View a user's movies
- `/users/<user_id>/movies/add` → Add a new movie (fetches details from OMDB API if available)
- `/users/<user_id>/movies/update/<movie_id>` → Update a movie
- `/error` → Error page
- `404.html` → Page not found

## License
This project is an assignment of my SE bootcamp Masterschool