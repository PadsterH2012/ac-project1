# AC-Project1: Flask User Management System

## Description
AC-Project1 is a simple Flask-based web application for user management. It provides basic functionality for user authentication and retrieval.

## Features
- User registration and login
- User data retrieval
- SQLite database integration

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

## Usage
1. Run the application:
   ```
   python wsgi.py
   ```
2. Open a web browser and navigate to `http://localhost:5000`

## Project Structure
- `app.py`: Main application file
- `routes.py`: Contains all route definitions
- `models.py`: Defines database models
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is open source and available under the [MIT License](LICENSE).
