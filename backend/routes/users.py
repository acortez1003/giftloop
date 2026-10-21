from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "username, email, and password are required"}), 400

    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return jsonify({"error": "email already registered"}), 409

    hashed_password = generate_password_hash(data['password'])

    new_user = User(
        username=data['username'],
        display_name=data.get('display_name', data['username']),
        email=data['email'],
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }), 201

@users_bp.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()

    if not data or not data.get('login') or not data.get('password'):
        return jsonify({"error": "username/email and password are required"}), 400

    existing = User.query.filter(
        (User.email == data['login']) |
        (User.username == data['login'])
    ).first()

    if not existing or not check_password_hash(existing.password, data['password']):
        return jsonify({"error": "invalid credentials"}), 401

    session['user_id'] = existing.id

    return jsonify({"id": existing.id, "username": existing.username}), 200

@users_bp.route('/api/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "not logged in"}), 401

    user = User.query.get(user_id)
    return jsonify({"id": user.id, "username": user.username}), 200