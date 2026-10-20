from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(225), nullable=False)

class ListMember(db.Model):
    __tablename__ = 'listmembers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    display_name = db.Column(db.String(80))

class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    recipient_listmember_id = db.Column(db.Integer, db.ForeignKey("listmembers.id"))
    name = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), unique=True, nullable=False)

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), unique=True, nullable=False)

class GroupMember(db.Model):
    __tablename__ = 'groupmembers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    display_name = db.Column(db.String(80))

class Gift(db.Model):
    __tablename__ = 'gifts'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2))
    link = db.Column(db.String(225))
    description = db.Column(db.String(500))
    image = db.Column(db.String(500))

class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.Integer, primary_key=True)
    gift_id = db.Column(db.Integer, db.ForeignKey("gifts.id"), nullable=False)
    listmember_id = db.Column(db.Integer, db.ForeignKey("listmembers.id"), nullable=False)
    status = db.Column(db.Enum("want_to_buy", "bought", name="claim_status"), nullable=False)