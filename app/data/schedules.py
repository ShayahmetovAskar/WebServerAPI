import sqlalchemy

from .db_session import SqlAlchemyBase, orm


class Schedule(SqlAlchemyBase):
    __tablename__ = 'schedules'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    class_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('classes.id'))
    class_ = orm.relationship('Class', back_populates='schedule')
    subjects = orm.relation('ScheduleSubject', back_populates='schedule')
