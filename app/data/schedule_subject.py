import sqlalchemy

from .db_session import SqlAlchemyBase, orm


class ScheduleSubject(SqlAlchemyBase):
    __tablename__ = 'schedule_subject'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    schedule_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('schedules.id'),
                                    index=True)
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('subjects.id'))
    day = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # День недели
    schedule = orm.relation('Schedule')
