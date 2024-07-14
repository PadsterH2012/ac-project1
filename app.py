from flask import Flask, request, jsonify
from models import db

import os
os.environ['FLASK_APP'] = 'app'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db.init_app(app)

@app.route("/login", methods=["POST"])
def login():
    # TO DO: Implement login logic here
    pass

if __name__ == "__main__":
    app.run(debug=True)
