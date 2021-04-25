import sqlalchemy

from .db_session import SqlAlchemyBase, orm

members_association_table = sqlalchemy.Table(
    'class_to_user',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('class', sqlalchemy.Integer, sqlalchemy.ForeignKey('classes.id')),
    sqlalchemy.Column('user', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
)

admins_association_table = sqlalchemy.Table(
    'class_to_admin',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('class', sqlalchemy.Integer, sqlalchemy.ForeignKey('classes.id')),
    sqlalchemy.Column('user', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
)


class Class(SqlAlchemyBase):
    __tablename__ = 'classes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer)
    subjects = orm.relationship('Subject', back_populates='class_')
    schedule = orm.relationship('Schedule', back_populates='class_')
    key = sqlalchemy.Column(sqlalchemy.String)
    members = orm.relation('User', secondary='class_to_user', backref='member_of')
    admins = orm.relation('User', secondary='class_to_admin', backref='admin_of')

