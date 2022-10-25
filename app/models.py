from itertools import count
from app import db, login
from datetime import datetime, time
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
import json


import app


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))
    posts = db.relationship('Post', backref = 'author', lazy='dynamic')
    about_me= db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)
    followed = db.relationship(
        'User', 
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers',lazy='dynamic'),
        lazy='dynamic')
    message_sent = db.relationship('Message',
        foreign_keys='Message.sender_id',
        backref='author', lazy='dynamic')
    message_received = db.relationship('Message',
        backref='recipient',
        foreign_keys='Message.recipient_id',
        lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    def __repr__(self) -> str:
        return f'User {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #the loader function keeps user in memory by retrieving user ID
    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed =  Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(
            followers.c.follower_id == self.id
        )
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password':self.id, 'ext': time()+expires_in},
        app.config['SECRET_KEY'],
        algorithm='HS56'
        )['reset_password']

    @staticmethod
    def verify_reset_token_password(token):
        try:
            id = jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256'])
        except:
            return 
        return User.query.get(id)
    
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)

        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

class Post(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default= datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'Post {self.body}'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    def __repr__(self):
        return f'<Message :{self.body}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Unix time format is the same around the whole world and it starts from 1.1.1970 as an epoch
    timestamp = db.Column(db.Float, index=True,default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
        

