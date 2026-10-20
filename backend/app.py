import os
from flask import Flask
from flask_migrate import Migrate
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/api/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')