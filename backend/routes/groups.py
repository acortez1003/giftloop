from flask import Blueprint, request, jsonify, session
from models import db, User, ListMember, List, Group, GroupMember, Gift, Claim
import secrets
from helpers import resolve_groupmember

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/api/groups', methods=['POST'])
def create_group():
    data = request.get_json()

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "must be logged in to create group"}), 401

    if not data or not data.get('name'):
        return jsonify({"error": "group name not provided"}), 400

    try:
        new_group = Group(
            owner_id = user_id,
            name = data['name'],
            token = secrets.token_urlsafe(16)
        )
        db.session.add(new_group)
        db.session.flush()

        new_groupmember = GroupMember(
            user_id = user_id,
            group_id = new_group.id
        )
        db.session.add(new_groupmember)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not create group"}), 500

    return jsonify({
        "id": new_group.id,
        "owner_id": new_group.owner_id,
        "name": new_group.name,
        "token": new_group.token,
        "needs_identity": not bool(user_id)
    }), 201

@groups_bp.route('/api/groups/<token>/join', methods=['POST'])
def join_group(token):
    group_obj = Group.query.filter_by(token=token).first()
    if not group_obj:
        return jsonify({"error": "group not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "data not provided"}), 400

    if data.get('existing_groupmember_id'):
        existing_guest = GroupMember.query.filter_by(
            id=data['existing_groupmember_id'],
            group_id=group_obj.id
        ).first()

        if not existing_guest:
            return jsonify({"error": "guest not found on this group"}), 404

        session[f'groupmember_id_{group_obj.id}'] = existing_guest.id
        return jsonify({
            "group": {"id": group_obj.id, "name": group_obj.name, "token": group_obj.token},
            "guest": {"id": existing_guest.id, "name": existing_guest.display_name}
        }), 200

    if not data.get('name'):
        return jsonify({"error": "name not provided"}), 400

    try:
        new_guest = GroupMember(
            group_id=group_obj.id,
            display_name=data['name']
        )
        db.session.add(new_guest)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not add guest"}), 500

    session[f'groupmember_id_{group_obj.id}'] = new_guest.id

    return jsonify({
        "group": {"id": group_obj.id, "name": group_obj.name, "token": group_obj.token},
        "guest": {"id": existing_guest.id, "name": existing_guest.display_name}
    }), 200

@groups_bp.route('/api/groups/<group_id>', methods=['DELETE'])
def delete_group(group_id):
    group_obj = Group.query.get(group_id)
    if not group_obj:
        return jsonify({"error": "group not found"}), 404

    user_id = session.get('user_id')
    if not user_id or user_id != group_obj.owner_id:
        return jsonify({"error": "unauthorized to delete group"}), 401

    try:
        db.session.delete(group_obj)
        db.session.commit
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not delete group"}), 500

    return jsonify({"message": "group deleted"}), 200

@groups_bp.route('/api/groups/<token>', methods=['GET'])
def get_group(token):
    group_obj = Group.query.filter_by(token=token).first()

    if not group_obj:
        return jsonify({"error": "group not found"}), 404

    member = resolve_groupmember(group_obj.id)
    if not member:
        existing_guests = GroupMember.query.filter_by(group_id=group_obj.id, user_id=None).all()
        return jsonify({
            "group": {"id": group_obj.id, "name": group_obj.name, "token": group_obj.token},
            "needs_identity": True,
            "existing_guests": [{"id": g.id, "display_name": g.display_name} for g in existing_guests],
        }), 200

    return jsonify({
        "group": {"id": group_obj.id, "name": group_obj.name, "token": group_obj.token},
        "needs_identity": False,
        "your_member_id": member.id,
    }), 200
