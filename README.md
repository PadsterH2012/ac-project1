# AC-Project1: Idea Incubator

## Description
AC-Project1 is a robust Flask-based web application called Idea Incubator. It provides essential functionality for user management, project planning, and AI-assisted development, all within a clean and intuitive interface. The application now features an enhanced chat interface with AI agents for project planning and writing, as well as improved project scope management.

## Features
- User registration with username, email, and password
- Secure user login and session management
- OAuth login support for Google and Facebook
- User dashboard for logged-in users
- User settings page for updating profile information
- User logout functionality
- User data retrieval API endpoint
- SQLite database integration for data persistence
- Responsive design with custom CSS styling
- AI Agent management system with customizable roles (e.g., Project Planner, Project Writer)
- Provider settings for AI services (including Ollama integration)
- Enhanced chat interface for interacting with AI agents
- Project management and planning tools
- Automatic project scope generation and updating
- Project journal for tracking conversations and decisions
- Backup and restore functionality for user data
- Virtual File System (VFS) for project organization

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
4. Set up AI providers in the Provider Settings page
5. Create and customize AI agents in the Agent Settings page
6. Create a new project or continue an existing one
7. Use the chat interface to interact with AI agents for project planning and writing
8. Explore the dashboard, projects, and other features

## Key Features
- User authentication and registration
- Project management and planning
- AI Agent creation and management with customizable roles
- Provider settings for AI services (e.g., Ollama)
- Agent role selection and customization (Project Planner, Project Writer)
- Enhanced interactive chat interface with AI agents
- Automatic project scope generation and updating
- Project journal for tracking conversations and decisions
- Backup and restore functionality for user data
- Virtual File System (VFS) for project organization

## API Endpoints
- GET `/users`: Retrieves a list of all users (username and ID)
- POST `/chat`: Sends a message to the AI agent and receives a response
- POST `/backup`: Creates a backup of user data
- POST `/restore`: Restores user data from a backup file
- POST `/clear_journal`: Clears the journal for a specific project

## Project Structure
- `app.py`: Main application file, sets up Flask and database
- `routes/`: Contains all route definitions and view functions
- `models/`: Defines database models (User, Project, Agent, Provider)
- `utils.py`: Utility functions for various operations
- `services/`: Contains service-related modules
  - `provider_connections/`: Handles connections to AI providers
  - `prompt_config/`: Stores default prompts for AI agents
  - `backup/`: Manages backup and restore functionality
- `templates/`: HTML templates for rendering pages
- `static/`: Static files (CSS, JavaScript, images)

## Security Features
- Passwords are hashed before storing in the database
- User sessions are managed securely
- CSRF protection is enabled by default in Flask
- OAuth integration for secure third-party authentication
- Email validation during registration
- Secure file handling for avatar uploads and backups
- API keys for AI providers are stored securely

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
- Werkzeug for password hashing and secure file handling
- Flask-OAuthlib for OAuth integration
- Google and Facebook for OAuth services
- Bootstrap for responsive design
- Ollama for AI integration
- Marked.js for Markdown rendering in the chat interface
