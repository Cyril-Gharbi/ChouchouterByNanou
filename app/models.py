from datetime import datetime, timezone

from flask_bcrypt import Bcrypt
from flask_login import UserMixin

from .extensions import db

bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(84), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    consent_privacy = db.Column(db.Boolean, nullable=False, default=False)
    consent_date = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
    is_approved = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)
    is_anonymized = db.Column(db.Boolean, default=False)

    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    admin = db.relationship("Admin", backref=db.backref("users", lazy=True))

    @property
    def is_active(self):
        return self.deleted_at is None

    def set_password(self, password):
        """Hash the password before storing it."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Check the password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"user-{self.id}"


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    username_at_time = db.Column(db.String(250), nullable=False)
    is_visible = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", backref=db.backref("comments", lazy=True))


class Admin(db.Model, UserMixin):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(84))
    email = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    def get_id(self):
        return f"admin-{self.id}"


class FidelityRewardLog(db.Model):
    __tablename__ = "fidelity_reward_log"

    id = db.Column(db.Integer, primary_key=True)
    fidelity_level = db.Column(db.Integer, default=0)
    fidelity_cycle = db.Column(db.Integer, default=0)
    level_reached = db.Column(db.Integer, nullable=False)  # 4 or 9
    date = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    cycle_number = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", backref="fidelity_reward_logs", passive_deletes=True)


class UserRequest(db.Model):
    __tablename__ = "user_requests"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(
        db.String(84),
        nullable=False,
    )
    requested_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def set_password(self, password):
        """Hash the password before storing it."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
