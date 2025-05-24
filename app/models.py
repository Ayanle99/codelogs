from datetime import datetime
from app import db, login
from flask_login import UserMixin
from flask import current_app


class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicit table name to avoid reserved keyword conflict

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    thumbnail_url = db.Column(db.String(256))

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'posts'  # Explicit table name for clarity and consistency

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # FK references users.id

    def is_short_post(self):
        return len(self.content) <= 140

    def __repr__(self):
        return f'<Post {self.content[:30]}...>'


class PostEditHistory(db.Model):
    __tablename__ = 'post_edit_histories'  # Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    diff = db.Column(db.Text, nullable=False)  # Unified diff format
    edited_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    post = db.relationship('Post', backref=db.backref('edit_history', lazy='dynamic'))

    def __repr__(self):
        return f'<EditHistory PostID={self.post_id} EditedAt={self.edited_at}>'


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
