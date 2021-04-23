import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    image_file = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='default.png')
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
