from app import create_app
import os

def main():
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')

if __name__ == '__main__':
    main()
