from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ListMember, List

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
        return jsonify({"error": "no assigned guest name and not logged in"}), 401

    user = User.query.get(user_id)
    return jsonify({"id": user.id, "username": user.username}), 200

@users_bp.route('/api/users/me/lists', methods=['GET'])
def get_user_lists():
    user_id = session.get('user_id')

    guest_member_ids_by_list = {}
    for key, value in session.items():
        if key.startswith('listmember_id_'):
            list_id = int(key.replace('listmember_id_', ''))
            guest_member_ids_by_list[list_id] = value

    if user_id:
        memberships = ListMember.query.filter_by(user_id=user_id).all()
        list_ids = [m.list_id for m in memberships]
        lists_by_id = {l.id: l for l in List.query.filter(List.id.in_(list_ids)).all()}
        pairs = [(lists_by_id[m.list_id], m.id) for m in memberships]
    else:  # guest
        lists = List.query.filter(List.id.in_(guest_member_ids_by_list.keys())).all()
        pairs = [(l, guest_member_ids_by_list[l.id]) for l in lists]

    own, joined = [], []
    for list_obj, member_id in pairs:
        if list_obj.recipient_listmember_id == member_id:
            own.append(list_obj)
        else:
            joined.append(list_obj)

    return  jsonify({
        "owned_lists": [{"id": l.id, "name": l.name, "token": l.token} for l in own],
        "joined_lists": [{"id": l.id, "name": l.name, "token": l.token} for l in joined]
    }), 200