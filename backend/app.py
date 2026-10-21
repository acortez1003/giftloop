import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from routes.users import users_bp
from routes.lists import lists_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

db.init_app(app)

app.register_blueprint(users_bp)
app.register_blueprint(lists_bp)

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')