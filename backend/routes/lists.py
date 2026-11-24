from flask import Blueprint, request, jsonify, session
from models import db, User, ListMember, List, Group, GroupMember, Gift, Claim
import secrets
from helpers import resolve_listmember, get_display_name

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('/api/lists', methods=['POST'])
def create_list():
    data = request.get_json()
    user_id = session.get('user_id')
    if not data or not data.get('name'):
        return jsonify({"error": "list name not provided"}), 400

    group_id = data.get('group_id')
    guest_group_member = None

    if group_id and not user_id:
        groupmember_id = session.get(f'groupmember_id_{group_id}')
        if not groupmember_id:
            return jsonify({"error": "must join group before creating a list in it"}), 401
        guest_group_member = GroupMember.query.get(groupmember_id)

    if group_id:
        lists = List.query.filter_by(group_id=group_id).all()
        for l in lists:
            if not l.recipient_listmember_id:
                continue

            if user_id:
                recipient = ListMember.query.get(l.recipient_listmember_id)
                if recipient.user_id == user_id:
                    return jsonify({"error": "can only have one list per group"}), 409
            else:
                guest_id = session.get(f'listmember_id_{l.id}')
                if l.recipient_listmember_id == guest_id:
                    return jsonify({"error": "can only have one list per group"}), 409

    try:
        new_list = List(
            group_id=group_id,
            name=data['name'],
            token=secrets.token_urlsafe(16)
        )
        db.session.add(new_list)
        db.session.flush()

        if user_id:
            new_listmember = ListMember(user_id=user_id, list_id=new_list.id)
        elif guest_group_member:
            new_listmember = ListMember(
                list_id=new_list.id,
                display_name=get_display_name(guest_group_member)
            )
        else:
            new_listmember = None

        if new_listmember:
            db.session.add(new_listmember)
            db.session.flush()
            new_list.recipient_listmember_id = new_listmember.id
            if not user_id:
                session[f'listmember_id_{new_list.id}'] = new_listmember.id

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not create list"}), 500

    return jsonify({
        "id": new_list.id,
        "group_id": new_list.group_id,
        "name": new_list.name,
        "token": new_list.token,
        "needs_identity": not bool(user_id or guest_group_member)
    }), 201


@lists_bp.route('/api/lists/<token>/join', methods=['POST'])
def join_list(token):
    list_obj = List.query.filter_by(token=token).first()
    if not list_obj:
        return jsonify({"error": "list not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "data not provided"}), 400

    # guest creating a list
    if not list_obj.recipient_listmember_id:
        if not data.get('display_name'):
            return jsonify({"error": "name required"}), 400

        try:
            owner_guest = ListMember(
                list_id=list_obj.id,
                display_name=data['display_name']
            )
            db.session.add(owner_guest)
            db.session.flush()

            list_obj.recipient_listmember_id = owner_guest.id
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "could not set up list owner"}), 500

        session[f'listmember_id_{list_obj.id}'] = owner_guest.id
        return jsonify({
            "list": {"id": list_obj.id, "name": list_obj.name, "token": list_obj.token},
            "guest": {"id": owner_guest.id, "name": owner_guest.display_name}
        }), 200

    # if user selects a guest from dropdown, add id to their session
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

    # otherwise, new guest and needs to enter a name
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
        "guest": {"id": new_guest.id, "name": new_guest.display_name}
    }), 200

@lists_bp.route('/api/lists/<list_id>', methods=['DELETE'])
def delete_list(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "list not found"}), 404

    member = resolve_listmember(list_obj.id)
    if not member or member.id != list_obj.recipient_listmember_id:
        return jsonify({"error": "unauthorized to delete this list"}), 401

    try:
        db.session.delete(list_obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not delete list"}), 500

    return jsonify({"message": "list deleted"}), 200

@lists_bp.route('/api/lists/<token>', methods=['GET'])
def get_list(token):
    list_obj = List.query.filter_by(token=token).first()

    if not list_obj:
        return jsonify({"error": "list not found"}), 404

    member = resolve_listmember(list_obj.id)
    if not member:
        existing_guests = ListMember.query.filter_by(list_id=list_obj.id, user_id=None).all()
        return jsonify({
            "list": {"id": list_obj.id, "name": list_obj.name, "token": list_obj.token},
            "needs_identity": True,
            "existing_guests": [{"id": g.id, "display_name": g.display_name} for g in existing_guests],
            "is_recipient": False
        }), 200

    name = get_display_name(member)

    is_recipient = member.id == list_obj.recipient_listmember_id

    return jsonify({
        "list": {"id": list_obj.id, "name": list_obj.name, "token": list_obj.token, "recipient_id": list_obj.recipient_listmember_id},
        "needs_identity": False,
        "your_member_id": member.id,
        "your_display_name": name,
        "is_recipient": is_recipient
    }), 200

@lists_bp.route('/api/groups/<token>/lists', methods=['GET'])
def get_group_lists(token):
    group_obj = Group.query.filter_by(token=token).first()
    if not group_obj:
        return jsonify({"error": "group not found"}), 404

    lists = List.query.filter_by(group_id=group_obj.id).all()

    user_id = session.get('user_id')

    my_list = None
    member_lists = []

    for l in lists:
        is_mine = False
        if l.recipient_listmember_id:
            if user_id:
                recipient = ListMember.query.get(l.recipient_listmember_id)
                is_mine = recipient.user_id == user_id
            else:
                guest_id = session.get(f'listmember_id_{l.id}')
                is_mine = guest_id == l.recipient_listmember_id

        if is_mine:
            my_list = l
        else:
            member_lists.append(l)

    return jsonify({
        "my_list": {"id": my_list.id, "name": my_list.name, "token": my_list.token} if my_list else None,
        "member_lists": [{"id": l.id, "name": l.name, "owner_name": get_display_name(ListMember.query.get(l.recipient_listmember_id)), "token": l.token} for l in member_lists]
    }), 200