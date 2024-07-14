# AC-Project1: Idea Incubator

## Description
AC-Project1 is a robust Flask-based web application called Idea Incubator. It provides essential functionality for user management, including user authentication, registration, and data retrieval, all within a clean and intuitive interface.

## Features
- User registration with username, email, and password
- Secure user login and session management
- OAuth login support for Google and Facebook
- User dashboard for logged-in users
- User logout functionality
- User data retrieval API endpoint
- SQLite database integration for data persistence
- Responsive design with custom CSS styling

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ac-project1.git
   cd ac-project1
   ```
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up the database:
   The application will automatically create the SQLite database file (`users.db`) when run for the first time.

## Usage
1. Run the application:
   ```
   python wsgi.py
   ```
2. Open a web browser and navigate to `http://localhost:5000`
3. Register a new account or log in with existing credentials
4. Explore the dashboard and logout functionality

## API Endpoints
- GET `/users`: Retrieves a list of all users (username and ID)

## Project Structure
- `app.py`: Main application file, sets up Flask and database
- `routes.py`: Contains all route definitions and view functions
- `models.py`: Defines database models (User)
- `templates/`: HTML templates for rendering pages
  - `base.html`: Base template with common structure
  - `index.html`: Home page with login and registration forms
  - `dashboard.html`: User dashboard page
- `static/`: Static files
  - `css/style.css`: Custom styles for the application
  - `js/main.js`: JavaScript file for potential future enhancements

## Security Features
- Passwords are hashed before storing in the database
- User sessions are managed securely
- CSRF protection is enabled by default in Flask
- OAuth integration for secure third-party authentication
- Email validation during registration

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements
- Flask and its extensions
- SQLAlchemy for database ORM
- Werkzeug for password hashing
- Flask-OAuthlib for OAuth integration
- Google and Facebook for OAuth services
