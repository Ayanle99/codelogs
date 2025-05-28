from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    posts = db.relationship(
        'Post',
        backref='author',
        lazy='dynamic',
        foreign_keys='Post.user_id'
    )

    edited_posts = db.relationship(
        'Post',
        backref='last_editor',
        lazy='dynamic',
        foreign_keys='Post.last_edited_by_id'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_post_user_id'),
        nullable=False
    )

    last_edited_by_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_post_last_edited_by_user'),
        nullable=True
    )

    last_edited_by = db.relationship('User', foreign_keys=[last_edited_by_id], lazy='joined')

    edit_histories = db.relationship(
        'EditHistory',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Post {self.title}>"


class EditHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id', name='fk_edit_history_post_id'),
        nullable=False,
        index=True
    )

    editor_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_edit_history_editor_id'),
        nullable=False,
        index=True
    )

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    diff = db.Column(db.Text, nullable=False)

    post = db.relationship('Post')  # Just a direct relationship, no backref here
    editor = db.relationship('User', lazy='joined')

    def __repr__(self):
        return f"<EditHistory post_id={self.post_id} editor_id={self.editor_id}>"


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
