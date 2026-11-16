from flask import session
from models import db, ListMember

# retrieves member object using list_id
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