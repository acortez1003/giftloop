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

    member = resolve_listmember()
    if not member:
        existing_guests = ListMember.query.filter_by(list_id=list_obj.id, user_id=None).all()
        return jsonify({
            "list": {"id": list_obj.id, "name": list_obj.name, "token": list_obj.token},
            "needs_identity": True,
            "existing_guest_names": [g.display_name for g in existing_guests]
        }), 200

    return jsonify({
        "list": {"id": list_obj.id, "name": list_obj.name, "token": list_obj.token},
        "needs_identity": False,
        "your_member_id": member.id
    }), 200

@lists_bp.route('/api/lists/<token>/join', methods=['POST'])
def join_list(token):
    list_obj = List.query.filter_by(token=token).first()
    if not list_obj:
        return jsonify({"error": "list not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "data not provided"}), 400

    if data.get('existing_listmember_id'):
        existing_guest = ListMember.query.filter_by(
            id=data['existing_listmember_id'],
            list_id=list_obj.id
        ).first()

        if not existing_guest:
            return jsonify({"error": "guest not found on this list"}), 404

        session[f'listmember_id_{list_obj.id}'] = existing_guest.id
        return jsonify({
            "list": {"id": list_obj.id, "name": list_obj.name, "token": list_obj.token},
            "guest": {"id": existing_guest.id, "name": existing_guest.display_name}
        }), 200

    if not data.get('name'):
        return jsonify({"error": "name not provided"}), 400

    try:
        new_guest = ListMember(
            list_id=list_obj.id,
            display_name=data['name']
        )
        db.session.add(new_guest)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not add guest"}), 500

    session[f'listmember_id_{list_obj.id}'] = new_guest.id

    return jsonify({
            "list": {"id": list_obj.id, "name": list_obj.name, "token": list_obj.token},
            "guest": {"id": existing_guest.id, "name": existing_guest.display_name}
    }), 200

def resolve_listmember(list_id):
    user_id = session.get('user_id')

    # registered user
    if user_id:
        existing = ListMember.query.filter(
            (ListMember.user_id == user_id) &
            (ListMember.list_id == list_id)
        ).first()

        if existing:
            return existing

        new_listmember = ListMember(
            user_id=user_id,
            list_id=list_id
        )
        db.session.add(new_listmember)
        db.session.commit()
        return new_listmember

    # guest visiting again
    listmember_id = session.get(f'listmember_id_{list_id}')
    if listmember_id:
        guest_member = ListMember.query.get(listmember_id)
        if guest_member:
            return guest_member

    # new guest / id not found
    return None