from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

def upgrade():
    db = SQLAlchemy(current_app)
    
    # Create a new temporary table with the updated schema
    db.engine.execute(text("""
    CREATE TABLE agent_new (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(50) NOT NULL,
        user_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        provider_id INTEGER NOT NULL,
        temperature FLOAT NOT NULL DEFAULT 0.7,
        system_prompt TEXT,
        FOREIGN KEY(user_id) REFERENCES user(id),
        FOREIGN KEY(project_id) REFERENCES project(id),
        FOREIGN KEY(provider_id) REFERENCES provider(id)
    )
    """))

    # Copy data from the old table to the new one
    db.engine.execute(text("""
    INSERT INTO agent_new (id, name, role, user_id, project_id, temperature, system_prompt)
    SELECT id, name, role, user_id, project_id, temperature, system_prompt
    FROM agent
    """))

    # Drop the old table
    db.engine.execute(text("DROP TABLE agent"))

    # Rename the new table to the original name
    db.engine.execute(text("ALTER TABLE agent_new RENAME TO agent"))

def downgrade():
    db = SQLAlchemy(current_app)
    
    # If you need to revert, you can drop the provider_id column
    # However, SQLite doesn't support dropping columns, so we'll need to recreate the table
    
    db.engine.execute(text("""
    CREATE TABLE agent_old (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(50) NOT NULL,
        user_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        temperature FLOAT NOT NULL DEFAULT 0.7,
        system_prompt TEXT,
        FOREIGN KEY(user_id) REFERENCES user(id),
        FOREIGN KEY(project_id) REFERENCES project(id)
    )
    """))

    db.engine.execute(text("""
    INSERT INTO agent_old (id, name, role, user_id, project_id, temperature, system_prompt)
    SELECT id, name, role, user_id, project_id, temperature, system_prompt
    FROM agent
    """))

    db.engine.execute(text("DROP TABLE agent"))
    db.engine.execute(text("ALTER TABLE agent_old RENAME TO agent"))
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

def upgrade():
    db = SQLAlchemy(current_app)
    
    # Add the provider_id column to the agent table
    db.engine.execute(text("ALTER TABLE agent ADD COLUMN provider_id INTEGER"))
    
    # Add the foreign key constraint
    db.engine.execute(text("CREATE INDEX ix_agent_provider_id ON agent (provider_id)"))
    db.engine.execute(text("CREATE TRIGGER fk_agent_provider_id BEFORE INSERT ON agent FOR EACH ROW BEGIN SELECT CASE WHEN ((SELECT id FROM provider WHERE id = NEW.provider_id) IS NULL) THEN RAISE(ABORT, 'Foreign Key Violation') END; END"))

def downgrade():
    db = SQLAlchemy(current_app)
    
    # Remove the foreign key constraint
    db.engine.execute(text("DROP TRIGGER IF EXISTS fk_agent_provider_id"))
    db.engine.execute(text("DROP INDEX IF EXISTS ix_agent_provider_id"))
    
    # Remove the provider_id column
    db.engine.execute(text("ALTER TABLE agent DROP COLUMN provider_id"))
