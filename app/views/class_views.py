from functools import wraps

from flask import Blueprint, render_template, redirect, abort, request
from flask_login import current_user, login_required

from app.data import db_session
from app.data.classes import Class
from app.data.schedule_subject import ScheduleSubject
from app.data.schedules import Schedule
from app.forms.add_class_form import ClassForm
from app.forms.add_schedule_days_form import AddScheduleDaysForm
from app.forms.add_schedule_lessons import WeekScheduleForm, DayScheduleForm


def check_admin(class_id):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    return current_user in class_.admins or current_user.id == class_.creator_id


class_views = Blueprint('class_views', __name__, static_folder='static', template_folder='templates')


@class_views.route('/add_class', methods=['GET', 'POST'])
@login_required
def add_class():
    form = ClassForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Class).filter(Class.name == form.name.data).first():
            return render_template('class/add_class.html', form=form,
                                   message='Название уже занято. Попробуйте другое')
        class_ = Class(
            name=form.name.data,
            key=form.key.data,
            creator_id=current_user.id,
        )
        db_sess.add(class_)
        db_sess.commit()
        return redirect(f'/class/{class_.id}')

    return render_template('class/add_class.html', form=form)


@class_views.route('/class/<int:class_id>')
@login_required
def view_class(class_id):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    schedule = db_sess.query(Schedule).filter(Schedule.class_id == class_id).first()
    day_to_subjects = None
    if schedule:
        day_to_subjects = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        for subj in schedule.subjects:
            day_to_subjects[subj.day].append(subj.name)
    is_admin = check_admin(class_id)
    return render_template('class/view_class.html', class_=class_, schedule=day_to_subjects,
                           is_admin=is_admin)


@class_views.route('/class/<int:class_id>/add_schedule/days')
@login_required
def add_schedule_days(class_id):
    if not check_admin(class_id):
        abort(404)
    form = AddScheduleDaysForm()
    if form.validate_on_submit():
        mon = form.mon.data
        tue = form.tue.data
        wed = form.wed.data
        thu = form.thu.data
        fri = form.fri.data
        sat = form.sat.data
        return redirect(
            f'/class/{class_id}/add_schedule/subjects/{mon}/{tue}/{wed}/{thu}/{fri}/{sat}')
    return render_template('class/add_schedule_days.html')


@class_views.route(
    '/class/<int:class_id>/add_schedule/subjects/<int:mon>/<int:tue>/<int:wed>/<int:thu>/<int:fri>/<int:sat>',
    methods=['GET', 'POST'])
@login_required
def subjects(class_id, mon, tue, wed, thu, fri, sat):
    if not check_admin(class_id):
        abort(404)
    num_subjects = [mon, tue, wed, thu, fri, sat]
    d = []
    for i in num_subjects:
        a = []
        for j in range(i):
            a.append({'name': ''})
        d.append({'subjects': a})
    weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    form = WeekScheduleForm(days=d)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        schedule = db_sess.query(Schedule).filter(Schedule.class_id == class_id).first()
        if not schedule:
            schedule = Schedule(class_id=class_id)
            db_sess.add(schedule)
            db_sess.commit()
            schedule = db_sess.query(Schedule).filter(Schedule.class_id == class_id).first()
        else:
            db_sess.query(ScheduleSubject).filter(
                ScheduleSubject.schedule == schedule).delete()
            db_sess.commit()

        for i in range(len(form.days.data)):
            for j in form.days.data[i]['subjects']:
                subject_name = j['name']
                schedule_subject = ScheduleSubject(
                    schedule_id=schedule.id,
                    name=subject_name,
                    day=(i + 1)
                )
                db_sess.add(schedule_subject)
        db_sess.commit()
        return redirect(f'class/{class_id}')
    return render_template('class/add_schedule_lessons.html', form=form, weekdays=weekdays,
                           num_subjects=num_subjects, class_id=class_id)
