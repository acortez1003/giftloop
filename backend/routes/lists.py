from flask import Blueprint, request, jsonify, session
from models import db, User, ListMember, List, Group, GroupMember, Gift, Claim
import secrets

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('/api/lists', methods=['POST'])
def create_list():
    data = request.get_json()

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "not logged in"}), 401

    if not data or not data.get('name'):
        return jsonify({"error": "list name not provided"}), 400

    try:
        new_list = List(
            name = data['name'],
            token = secrets.token_urlsafe(16)
        )
        db.session.add(new_list)
        db.session.flush()

        new_listmember = ListMember(
            user_id = user_id,
            list_id = new_list.id,
        )
        db.session.add(new_listmember)
        db.session.flush()

        new_list.recipient_listmember_id = new_listmember.id

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not create list"}), 500

    return jsonify({
        "id": new_list.id,
        "name": new_list.name,
        "token": new_list.token
    }), 201

@lists_bp.route('/api/lists/<token>', methods=['GET'])
def get_list(token):
    list_obj = List.query.filter_by(token=token).first()

    if not list_obj:
        return jsonify({"error": "list not found"}), 404

    return jsonify({
        "id": list_obj.id,
        "name": list_obj.name,
        "token": list_obj.token
    }), 200