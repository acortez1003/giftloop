import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from models import db
from routes.users import users_bp
from routes.lists import lists_bp
from routes.gifts import gifts_bp
from routes.claims import claims_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

db.init_app(app)

app.register_blueprint(users_bp)
app.register_blueprint(lists_bp)
app.register_blueprint(gifts_bp)
app.register_blueprint(claims_bp)

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')