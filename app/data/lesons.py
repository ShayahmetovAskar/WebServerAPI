import sqlalchemy
from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('subjects.id'),
                                   nullable=False)
    homework = sqlalchemy.Column(sqlalchemy.String)
    date_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
