from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sqlalchemy import and_

allowed_viewers = db.Table(
    'allowed_viewers',
    db.Column('owner_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('viewer_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


followers = db.Table(
    'followers',
    db.metadata,
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'),
              primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'),
              primary_key=True),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)

)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    bio = db.Column(db.Text, nullable=True)

    thumbnail_url = db.Column(db.String(255), nullable=True)

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

    is_private = db.Column(db.Boolean, default=False, nullable=True)

    # Users this user allows to view their private profile
    allowed_users = db.relationship(
        'User',
        secondary=allowed_viewers,
        primaryjoin=(allowed_viewers.c.owner_id == id),
        secondaryjoin=(allowed_viewers.c.viewer_id == id),
        backref=db.backref('can_view', lazy='dynamic'),
        lazy='dynamic'
    )

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)  # this adds to the followers table

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)  # this removes from the association table

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


    def recent_following(self, limit=10):
        return (
            FollowEvent.query
            .filter_by(follower_id=self.id, action='follow')
            .order_by(FollowEvent.timestamp.desc())
            .limit(limit)
            .all()
        )

    def recent_followers(self, limit=10):
        return (
            FollowEvent.query.filter_by(followed_id=self.id, action='follow')
            .order_by(FollowEvent.timestamp.desc())
            .limit(limit)
            .all()
        )

    def recent_unfollowed_by_user(self, limit=10):
        return (
            FollowEvent.query
                .filter(FollowEvent.follower_id == self.id, FollowEvent.action == 'unfollow')
                .order_by(FollowEvent.timestamp.desc())
                .limit(limit)
                .all()
        )


    @property
    def get_followers_count(self):
        return self.followers.count()


    @property
    def get_following_count(self):
        return self.followed.count()

    # max follows paul
    # test follows paul
    # if max goes to test user profille, both max and test have mutual
    def mutuals(self, other_user):
        """Get users that both this user and other_user follow"""
        if not other_user:
            return []

        # Simple and clean approach
        my_following = set(self.followed.all())
        other_following = set(other_user.followed.all())
        return list(my_following.intersection(other_following))

    def has_mutual_following(self, other_user, target_user):
        """Check if both users follow a specific target user"""
        return target_user in self.mutuals(other_user)


    @property
    def is_online(self):
        if not self.last_seen:
            return False
        now = datetime.utcnow()
        delta = now - self.last_seen
        return delta.total_seconds() < 300  # 5 minutes threshold


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def are_they_friends(self, other_user):
        """Return True if both users follow each other"""
        if not other_user:
            return False
        return self.is_following(other_user) and other_user.is_following(self)

    def __repr__(self):
        return f"<User {self.username}>"




class FollowEvent(db.Model):
    __tablename__ = 'follow_events'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # "follow" or "unfollow"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='follow_events_sent')
    followed = db.relationship('User', foreign_keys=[followed_id], backref='follow_events_received')


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


    @property
    def is_edited(self):
        return self.updated_at is not None

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

