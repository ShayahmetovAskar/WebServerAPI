import sqlalchemy
from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('subjects.id'),
                                   nullable=False)
    homework = sqlalchemy.Column(sqlalchemy.String)
    class_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('classes.id'),
                                 nullable=False, index=True)
    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, index=True)
    week = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, index=True)
    day = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
