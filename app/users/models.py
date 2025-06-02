from app import db
from app.models import *


class ProfileViewRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profile_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='pending')  # e.g. pending, approved, denied

    approved = db.Column(db.Boolean, default=False)
    ignored = db.Column(db.Boolean, default=False)

    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_view_requests')
    profile_owner = db.relationship('User', foreign_keys=[profile_owner_id], backref='received_view_requests')


