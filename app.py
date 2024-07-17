from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')

@app.cli.command("db_migrate")
def db_migrate():
    from app.migrations import add_provider_id_to_agent
    add_provider_id_to_agent.upgrade()
