import sqlalchemy
from .db_session import SqlAlchemyBase, orm


class Subject(SqlAlchemyBase):
    __tablename__ = 'subjects'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    class_id = sqlalchemy.Column(sqlalchemy.ForeignKey('classes.id'))
    class_ = orm.relationship('Class', back_populates='subjects')
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)

