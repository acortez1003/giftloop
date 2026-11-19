from flask import Blueprint, request, jsonify, session
from models import db, User, ListMember, List, Group, GroupMember, Gift, Claim
from helpers import resolve_listmember

claims_bp = Blueprint('claims', __name__)

@claims_bp.route('/api/gifts/<gift_id>/claims', methods=['GET'])
def get_gift_claims(gift_id):
    gift_obj = Gift.query.get(gift_id)
    if not gift_obj:
        return jsonify({"error": "gift not found"}), 404

    list_obj = List.query.get(gift_obj.list_id)
    user = resolve_listmember(list_obj.id)
    if not list_obj or user.id == list_obj.recipient_listmember_id:
        return jsonify({"error:": "unauthorized to get claims"}), 401

    claims = Claim.query.filter_by(gift_id=gift_obj.id).all()

    return jsonify({
        "claims": [{"id": l.id, "gift_id": l.gift_id, "claimed_by": l.listmember_id, "status": l.status} for l in claims]
    }), 201

@claims_bp.route('/api/gifts/<gift_id>/claims', methods=['POST'])
def add_claim(gift_id):
    data = request.get_json()

    gift_obj = Gift.query.get(gift_id)
    if not gift_obj:
        return jsonify({"error": "gift not found"}), 404

    list_obj = List.query.get(gift_obj.list_id)

    member = resolve_listmember(list_obj.id)
    if not member or member.id == list_obj.recipient_listmember_id:
        return jsonify({"error": "unauthorized to make claim"}), 401

    if not data or not data.get('status'):
        return jsonify({"error": "please make valid claim"}), 400

    # toggle status
    claim_obj = Claim.query.filter_by(gift_id=gift_obj.id, listmember_id=member.id).first()
    if claim_obj:
        current_status = claim_obj.status
        try:
            db.session.delete(claim_obj)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "could not edit claim"}), 500
        if data['status'] == current_status:
            return jsonify({"message": "claim removed"}), 201

    try:
        new_claim = Claim(
            gift_id = gift_obj.id,
            listmember_id = member.id,
            status = data['status']
        )
        db.session.add(new_claim)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "could not add claim"}), 500

    return jsonify({
        "id": new_claim.id, 
        "gift_id": new_claim.gift_id, 
        "claimed_by_id": new_claim.listmember_id, 
        "status": new_claim.status
    }), 201
