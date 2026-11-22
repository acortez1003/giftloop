from flask import session
from models import db, List, ListMember, GroupMember

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
    list_obj = List.query.get(list_id)
    # guest is coming from a group, lazy add
    if list_obj.group_id:
        groupmember_id = session.get(f'groupmember_id_{list_obj.group_id}')
        if groupmember_id:
            groupmember_obj = GroupMember.query.get(groupmember_id)
            if groupmember_obj:
                new_listmember = ListMember(
                    list_id=list_id,
                    display_name=groupmember_obj.display_name
                )
                db.session.add(new_listmember)
                db.session.commit()
                session[f'listmember_id_{list_id}'] = new_listmember.id
                return new_listmember

    return None

def resolve_groupmember(group_id):
    user_id = session.get('user_id')

    if user_id:
        existing = GroupMember.query.filter(
            (GroupMember.user_id == user_id) &
            (GroupMember.group_id == group_id)
        ).first()

        if existing:
            return existing

        new_groupmember = GroupMember(
            user_id=user_id,
            group_id=group_id
        )
        db.session.add(new_groupmember)
        db.session.commit()
        return new_groupmember

    groupmember_id = session.get(f'groupmember_id_{group_id}')
    if groupmember_id:
        guest_member = GroupMember.query.get(groupmember_id)
        if guest_member:
            return guest_member

    return None