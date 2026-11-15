from flask import Blueprint, request, jsonify, session
from models import db, User, ListMember, List, Group, GroupMember, Gift, Claim
from helpers import resolve_listmember

gifts_bp = Blueprint('gifts', __name__)

@gifts_bp.route('/api/lists/<token>/gifts', methods=['GET'])
def get_list_gifts(token):
    list_obj = List.query.filter_by(token=token).first()

    if not list_obj:
        return jsonify({"error": "list not found"}), 404

    gifts = Gift.query.filter_by(list_id=list_obj.id).all()

    return jsonify({
        "gifts": [{"id": l.id, "name": l.name, "price": l.price, "link": l.link, "description": l.description, "image": l.image} for l in gifts]
    }), 200


@gifts_bp.route('/api/lists/<token>/gifts', methods=['POST'])
def add_gift(token):
    data = request.get_json()
    list_obj = List.query.filter_by(token=token).first()

    if not list_obj:
        return jsonify({"error": "list not found"}), 404

    member = resolve_listmember(list_obj.id)
    if not member or member.id != list_obj.recipient_listmember_id:
        return jsonify({"error": "unauthorized to add gift"}), 401

    if not data or not data.get('name'):
        return jsonify({"error": "please enter a gift name"}), 400

    try:
        new_gift = Gift(
            list_id=list_obj.id,
            name=data['name'],
            price=data.get('price'),
            link=data.get('link'),
            description=data.get('description'),
            image=data.get('image')
        )
        db.session.add(new_gift)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not add gift"}), 500

    return jsonify({"id": new_gift.id, "name": new_gift.name}), 201