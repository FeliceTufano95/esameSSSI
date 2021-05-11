from DB import db
from flask import Flask
app = Flask(__name__)

with app.app_context():
        db.init_app(app)
        db.init_db()