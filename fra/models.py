from . import db, app, lm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import AnonymousUserMixin

import hashlib
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from data import clients, product_areas


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), index=True)
    last_name = db.Column(db.String(255), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    phone = db.Column(db.String(128),  index=True)
    image = db.Column(db.String(500),  index=True)
    password_hash = db.Column(db.String(128))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    allowed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    features = db.relationship('Feature', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def set_image(self, image):
        if image:
            self.image = image
        else:
            self.image = 'default.jpg'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

lm.anonymous_user = AnonymousUser


class Feature(db.Model):
    __tablename__ = 'features'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(256))
    description = db.Column(db.Text)
    target_date = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    priority = db.Column(db.Integer)
    product_area_id = db.Column(db.Integer, db.ForeignKey('product_areas.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def adjust_priorities(client, priority):
        # I could have used this query, but its buggy
        # client_features = Feature.query.filter_by(
        #     client=client).filter(priority >= priority)
        client_features = Feature.query.filter_by(client=client).all()
        for feature in client_features:
            if feature.priority >= priority:
                feature.priority += 1
                db.session.add(feature)
                db.session.commit()

    @staticmethod
    def priority_exists(client, priority):
        client_feature = Feature.query.filter_by(
            client=client).filter_by(priority=priority).limit(1)
        return client_feature.count() > 0


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    features = db.relationship('Feature', backref='client', lazy='dynamic')

    @staticmethod
    def insert_clients():
        for client in clients:
            c = Client.query.filter_by(name=client).first()
            if c is None:
                c = Client(name=client)
            db.session.add(c)
            db.session.commit()


class ProductArea(db.Model):
    __tablename__ = 'product_areas'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256))
    features = db.relationship(
        'Feature', backref='product_area', lazy='dynamic')
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def insert_product_areas():
        for area in product_areas:
            a = ProductArea.query.filter_by(name=area).first()
            if a is None:
                a = ProductArea(name=area)
            db.session.add(a)
            db.session.commit()


class Permission:
    USER = 0x02
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.USER, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name
