import datetime
from functools import wraps

from flask import Blueprint, render_template, redirect, abort, request
from flask_login import current_user, login_required

from app.data import db_session
from app.data.classes import Class
from app.data.lesons import Lesson
from app.data.schedule_subject import ScheduleSubject
from app.data.schedules import Schedule
from app.data.sujbects import Subject
from app.data.users import User
from app.forms.add_class_form import ClassForm
from app.forms.add_lesson_form import AddLessonForm
from app.forms.add_schedule_days_form import AddScheduleDaysForm
from app.forms.add_schedule_lessons import WeekScheduleForm
from app.forms.add_subject_amount import AddSubjectsAmount
from app.forms.add_subjects import SubjectsForm
from app.forms.join_class_form import JoinClassForm


def check_admin(class_id, user=current_user):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    is_admin = user in class_.admins
    db_sess.close()
    return is_admin


# Проверка на правильность ID класса
def correct_class_id(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db_sess = db_session.create_session()
        class_ = db_sess.query(Class).get(kwargs['class_id'])
        if not class_:
            db_sess.close()
            return abort(404)
        db_sess.close()
        return f(*args, **kwargs)

    return decorated_function


# Состоит ли текущий пользователь в классе
def membership_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db_sess = db_session.create_session()
        class_ = db_sess.query(Class).get(kwargs['class_id'])
        if current_user not in class_.members:
            db_sess.close()
            return redirect(f'/class/{kwargs["class_id"]}/join')
        db_sess.close()
        return f(*args, **kwargs)

    return decorated_function


# Является ли текущий пользователь администратором класса
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db_sess = db_session.create_session()
        class_ = db_sess.query(Class).get(kwargs['class_id'])
        if current_user not in class_.admins:
            db_sess.close()
            return abort(404)
        db_sess.close()
        return f(*args, **kwargs)

    return decorated_function


# Класс-помощник работы с датами
class DateHelper:
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября',
              'октября', 'ноября', 'декабря']

    @staticmethod
    def get_current_date():
        today = datetime.datetime.today()
        y, w, _ = today.isocalendar()
        return y, w

    # Прибавить неделю к текущей дате
    @staticmethod
    def add_week(y, w):
        date = datetime.datetime.strptime(f'{y} {w} {1}', '%G %V %u')
        date += datetime.timedelta(weeks=1)
        y, w, _ = date.isocalendar()
        return y, w

    # Отнять неделю от текущей даты
    @staticmethod
    def subtract_week(y, w):
        date = datetime.datetime.strptime(f'{y} {w} {1}', '%G %V %u')
        date -= datetime.timedelta(weeks=1)
        y, w, _ = date.isocalendar()
        return y, w

    # Форматированный вывод даты
    @staticmethod
    def formatted_dates(y, w):
        date = datetime.datetime.strptime(f'{y} {w} {1}', '%G %V %u')
        formatted = []
        for _ in range(1, 7):
            formatted.append(date.strftime("%d.%m.%y"))
            date += datetime.timedelta(days=1)
        return formatted


class_views = Blueprint('class_views', __name__, static_folder='static', template_folder='templates')


# Назначение администратором класса
@class_views.route('/class/<int:class_id>/set_admin/<int:user_id>')
@login_required
@correct_class_id
def set_admin(class_id, user_id):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    if current_user.id != class_.creator_id or current_user.id == user_id:
        db_sess.close()
        return abort(404)
    user = db_sess.query(User).get(user_id)
    if not user:
        db_sess.close()
        return abort(404)
    class_.admins.append(user)
    db_sess.commit()
    db_sess.close()
    return redirect(f'/class/{class_id}')


# Разжалование администратора класса
@class_views.route('/class/<int:class_id>/unset_admin/<int:user_id>')
@login_required
@correct_class_id
def unset_admin(class_id, user_id):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    if current_user.id != class_.creator_id or user_id == current_user.id:
        db_sess.close()
        return abort(404)
    user = db_sess.query(User).get(user_id)
    if not user:
        db_sess.close()
        return abort(404)
    if user in class_.admins:
        class_.admins.remove(user)
    db_sess.commit()
    db_sess.close()
    return redirect(f'/class/{class_id}')


# Изгнание из класса
@class_views.route('/class/<int:class_id>/kick/<int:user_id>')
@login_required
@correct_class_id
@membership_required
def kick(class_id, user_id):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    user = db_sess.query(User).get(user_id)
    if not class_ or not user:
        db_sess.close()
        return abort(404)
    if (
            user in class_.admins and current_user.id != class_.creator_id) or user_id == class_.creator_id:
        db_sess.close()
        return abort(404)
    if current_user not in class_.admins and user.id != current_user.id:
        db_sess.close()
        return abort(404)
    class_.members.remove(user)
    db_sess.commit()
    db_sess.close()
    return redirect(f'/class/{class_id}')


# Добавление нового класса
@class_views.route('/add_class', methods=['GET', 'POST'])
@login_required
def add_class():
    form = ClassForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Class).filter(Class.name == form.name.data).first():
            return render_template('class/add_class.html', form=form,
                                   message='Название уже занято. Попробуйте другое',
                                   header='Добавление класса')
        class_ = Class(
            name=form.name.data,
            key=form.key.data,
            creator_id=current_user.id,
        )
        current_user_ = db_sess.query(User).get(current_user.id)
        class_.admins.append(current_user_)
        class_.members.append(current_user_)
        db_sess.add(class_)
        db_sess.commit()
        class_id = class_.id
        db_sess.close()

        return redirect(f'/class/{class_id}')

    return render_template('class/add_class.html', form=form, header='Добавление класса')


# Главная страница класса
@class_views.route('/class/<int:class_id>')
@login_required
@correct_class_id
@membership_required
def view_class(class_id):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).filter(Class.id == class_id).first()
    schedule = db_sess.query(Schedule).filter(Schedule.class_id == class_id).first()
    members = []
    for member in class_.members:
        status = ''
        if member.id == class_.creator_id:
            status = 'Создатель'
        elif check_admin(class_id, member):
            status = 'Администратор'
        members.append([member.username, status, member.id])
    class_subjects = db_sess.query(Subject).with_entities(Subject.name).filter(
        Subject.class_id == class_id).all()
    class_subjects = [i[0] for i in class_subjects]
    day_to_subjects = None
    if schedule:
        day_to_subjects = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        for subj in schedule.subjects:
            subj_name = db_sess.query(Subject).with_entities(Subject.name).filter(
                Subject.id == subj.subject_id).first()
            day_to_subjects[subj.day].append(subj_name[0])
    is_admin = check_admin(class_id)
    is_creator = class_.creator_id == current_user.id
    db_sess.close()
    y, w = DateHelper.get_current_date()
    diary_url = f'/class/{class_id}/diary/{y}/{w}'
    return render_template('class/view_class.html', class_=class_, schedule=day_to_subjects,
                           is_admin=is_admin, is_creator=is_creator, members=members,
                           class_subjects=class_subjects, url_join=request.url + '/join',
                           diary_url=diary_url)


# Ввод количества уроков в расписании
@class_views.route('/class/<int:class_id>/add_schedule/days', methods=["GET", "POST"])
@login_required
@correct_class_id
@admin_required
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
    return render_template('class/add_schedule_days.html', form=form)


# Ввод предметов в расписание
@class_views.route('/class/<int:class_id>/add_schedule/subjects/<int:mon>'
                   '/<int:tue>/<int:wed>/<int:thu>/<int:fri>/<int:sat>',
                   methods=['GET', 'POST'])
@login_required
@correct_class_id
@admin_required
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
    db_sess = db_session.create_session()
    subjects_list = db_sess.query(Subject).with_entities(Subject.id, Subject.name).filter(
        Subject.class_id == class_id).all()
    db_sess.close()
    subjects_list = [(i[0], i[1]) for i in subjects_list]
    subjects_list.insert(0, ("", "---"))
    form = WeekScheduleForm(days=d)
    for i in form.days.entries:
        for j in i.subjects.entries:
            j.name_.choices = subjects_list
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

        for i in range(len(form.days.entries)):
            for j in form.days.entries[i].subjects.entries:
                schedule_subject = ScheduleSubject(
                    schedule_id=schedule.id,
                    subject_id=j.name_.data,
                    day=(i + 1)
                )
                db_sess.add(schedule_subject)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/class/{class_id}')
    return render_template('class/add_schedule_lessons.html', form=form, weekdays=weekdays,
                           num_subjects=num_subjects, class_id=class_id)


# Ссылка-приглашение в класс
@class_views.route('/class/<int:class_id>/join', methods=["GET", "POST"])
@login_required
@correct_class_id
def join_class(class_id):
    form = JoinClassForm()
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)

    if form.validate_on_submit():
        if form.key.data == class_.key:
            current_user_ = db_sess.query(User).get(current_user.id)
            class_.members.append(current_user_)
            db_sess.commit()
            db_sess.close()
            return redirect(f'/class/{class_id}')
        else:
            db_sess.close()
            return render_template('class/join_class.html', form=form, message='Неверный ключ')

    if request.method == 'GET':
        if current_user in class_.members:
            db_sess.close()
            return redirect(f'/class/{class_id}')
        db_sess.close()
        return render_template('class/join_class.html', form=form)


# Ввод количества предметов класса
@class_views.route('/class/<int:class_id>/add_subjects/amount', methods=['GET', 'POST'])
@login_required
@correct_class_id
@admin_required
def add_subject_amount(class_id):
    form = AddSubjectsAmount()
    if form.validate_on_submit():
        amount = form.amount.data
        return redirect(f'/class/{class_id}/add_subjects/{amount}')
    return render_template('class/add_subjects_amount.html', form=form)


# Ввод предметов класса
@class_views.route('/class/<int:class_id>/add_subjects/<int:amount>', methods=['GET', 'POST'])
@login_required
@correct_class_id
@admin_required
def add_subjects(class_id, amount):
    d = []
    for i in range(amount):
        d.append({'name': ''})
    form = SubjectsForm(subjects=d)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        db_sess.query(Subject).filter(Subject.class_id == class_id).delete()
        for subj in form.subjects.data:
            subject = Subject(name=subj['name'], class_id=class_id)
            db_sess.add(subject)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/class/{class_id}')

    return render_template('class/add_subjects.html', form=form)


# Просмотр дневника
@class_views.route('/class/<int:class_id>/diary/<int:year>/<int:week>')
@login_required
@correct_class_id
@membership_required
def view_diary(class_id, year, week):
    db_sess = db_session.create_session()
    lessons = db_sess.query(Lesson).with_entities(Lesson.day, Lesson.subject_id, Lesson.homework). \
        filter(Lesson.year == year, Lesson.week == week, Lesson.class_id == class_id).all()
    day_to_lesson = [[] for _ in range(6)]
    for item in lessons:
        subject = db_sess.query(Subject).with_entities(Subject.name). \
            filter(Subject.id == item[1]).first()
        day_to_lesson[item[0] - 1].append([subject[0], item[2]])
    db_sess.close()
    is_admin = check_admin(class_id)
    y_p, w_p = DateHelper.subtract_week(year, week)
    prev_url = f'/class/{class_id}/diary/{y_p}/{w_p}'
    y_n, w_n = DateHelper.add_week(year, week)
    next_url = f'/class/{class_id}/diary/{y_n}/{w_n}'
    edit_url = f'/class/{class_id}/diary/{year}/{week}/edit'
    formatted_date = DateHelper.formatted_dates(year, week)
    back_url = f'/class/{class_id}'
    weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    return render_template('class/diary.html', lessons=day_to_lesson, is_admin=is_admin,
                           next_url=next_url, prev_url=prev_url, edit_url=edit_url,
                           formatted_date=formatted_date, weekdays=weekdays, back_url=back_url)


# Редактирование дневника
@class_views.route('/class/<int:class_id>/diary/<int:year>/<int:week>/edit')
@login_required
@correct_class_id
@admin_required
def edit_diary(class_id, year, week):
    db_sess = db_session.create_session()
    lessons = db_sess.query(Lesson).with_entities(
        Lesson.id, Lesson.day, Lesson.subject_id, Lesson.homework). \
        filter(Lesson.year == year, Lesson.week == week, Lesson.class_id == class_id).all()
    day_to_lesson = [[] for _ in range(6)]
    for item in lessons:
        subject = db_sess.query(Subject).with_entities(Subject.name). \
            filter(Subject.id == item[2]).first()
        day_to_lesson[item[1] - 1].append([subject[0], item[3], item[0]])
    db_sess.close()
    weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    back_url = f'/class/{class_id}/diary/{year}/{week}'
    fill_schedule_url = f'/class/{class_id}/diary/fill_schedule/{year}/{week}/'
    delete_schedule_url = f'/class/{class_id}/diary/delete_schedule/{year}/{week}'
    formatted_date = DateHelper.formatted_dates(year, week)
    return render_template('class/edit_diary.html', lessons=day_to_lesson, class_id=class_id,
                           weekdays=weekdays, year=year, week=week, back_url=back_url,
                           fill_schedule_url=fill_schedule_url, formatted_date=formatted_date,
                           delete_schedule_url=delete_schedule_url)


# Добавление урока в дневник
@class_views.route('/class/<int:class_id>/diary/add_lesson/<int:year>/<int:week>/<int:day>',
                   methods=['GET', 'POST'])
@login_required
@correct_class_id
@admin_required
def add_lesson(class_id, year, week, day):
    if request.method == 'GET':
        form = AddLessonForm()
        db_sess = db_session.create_session()
        subjects = db_sess.query(Subject).with_entities(Subject.id, Subject.name).filter(
            Subject.class_id == class_id).all()
        subjects = [(i[0], i[1]) for i in subjects]
        subjects.insert(0, ("", "---"))
        form.lesson.choices = subjects
        db_sess.close()
        return render_template('class/add_lesson.html', form=form, title='Добавление поля')
    else:
        db_sess = db_session.create_session()
        form = request.form
        lesson = Lesson(
            subject_id=form['lesson'],
            homework=form['homework'],
            class_id=class_id,
            year=year,
            week=week,
            day=day
        )
        db_sess.add(lesson)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/class/{class_id}/diary/{year}/{week}/edit')


# Изменение урока дневника
@class_views.route('/class/<int:class_id>/diary/edit_lesson/<int:lesson_id>',
                   methods=['GET', 'POST'])
@login_required
@correct_class_id
@admin_required
def edit_lesson(class_id, lesson_id):
    if request.method == 'GET':
        form = AddLessonForm()
        db_sess = db_session.create_session()
        lesson = db_sess.query(Lesson).get(lesson_id)
        if not lesson:
            db_sess.close()
            return abort(404)
        subjects = db_sess.query(Subject).with_entities(Subject.id, Subject.name).filter(
            Subject.class_id == class_id).all()
        subjects = [(i[0], i[1]) for i in subjects]
        form.lesson.choices = subjects
        form.lesson.default = lesson.subject_id
        form.process()
        form.homework.data = lesson.homework
        db_sess.close()
    else:
        db_sess = db_session.create_session()
        lesson = db_sess.query(Lesson).get(lesson_id)
        lesson.subject_id = request.form['lesson']
        lesson.homework = request.form['homework']
        db_sess.commit()
        year, week = lesson.year, lesson.week
        db_sess.close()
        return redirect(f'/class/{class_id}/diary/{year}/{week}/edit')

    return render_template('class/add_lesson.html', form=form, title='Изменение поля')


# Удаление урока
@class_views.route('/class/<int:class_id>/diary/delete_lesson/<int:lesson_id>', methods=['GET'])
@login_required
@correct_class_id
@admin_required
def delete_lesson(class_id, lesson_id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).get(lesson_id)
    if not lesson:
        db_sess.close()
        return abort(404)
    year, week = lesson.year, lesson.week
    db_sess.delete(lesson)
    db_sess.commit()
    db_sess.close()
    return redirect(f'/class/{class_id}/diary/{year}/{week}/edit')


# Заполнение недели расписанием
@class_views.route('/class/<int:class_id>/diary/fill_schedule/<int:year>/<int:week>/')
@login_required
@correct_class_id
@admin_required
def fill_in_schedule(class_id, year, week):
    db_sess = db_session.create_session()
    schedule = db_sess.query(Schedule).filter(Schedule.class_id == class_id).first()
    if not schedule:
        db_sess.close()
        return redirect(f'/class/{class_id}/diary/{year}/{week}/edit')
    db_sess.query(Lesson).filter(Lesson.class_id == class_id, Lesson.year == year,
                                 Lesson.week == week).delete()
    db_sess.commit()
    for item in schedule.subjects:
        lesson = Lesson(
            subject_id=item.subject_id,
            class_id=class_id,
            year=year,
            week=week,
            homework='',
            day=item.day
        )
        db_sess.add(lesson)
    db_sess.commit()
    db_sess.close()
    return redirect(f'/class/{class_id}/diary/{year}/{week}/edit')


# Удаление расписания с данной недели
@class_views.route('/class/<int:class_id>/diary/delete_schedule/<int:year>/<int:week>/')
@login_required
@correct_class_id
@admin_required
def delete_schedule(class_id, year, week):
    db_sess = db_session.create_session()
    db_sess.query(Lesson).filter(Lesson.class_id == class_id, Lesson.year == year,
                                 Lesson.week == week).delete()
    db_sess.commit()
    db_sess.close()
    return redirect(f'/class/{class_id}/diary/{year}/{week}/edit')


# Изменение параметров класса
@class_views.route('/class/<int:class_id>/settings', methods=['GET', 'POST'])
@login_required
@correct_class_id
def class_settings(class_id):
    form = ClassForm()
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    if form.validate_on_submit():
        class_.name = form.name.data
        class_.key = form.key.data
        db_sess.commit()
        db_sess.close()
        return redirect(f'/class/{class_id}')
    form.name.data = class_.name
    form.key.data = class_.key
    url_delete = request.url + '/delete'
    db_sess.close()
    return render_template('class/add_class.html', show_delete=True, form=form,
                           header='Изменение Класса', url_delete=url_delete)


# Удаление класса
@class_views.route('/class/<int:class_id>/settings/delete', methods=['GET'])
@login_required
@correct_class_id
@admin_required
def delete_class(class_id):
    db_sess = db_session.create_session()
    class_ = db_sess.query(Class).get(class_id)
    if current_user.id != class_.creator_id:
        return abort(404)
    db_sess.delete(class_)
    db_sess.query(Lesson).filter(Lesson.class_id == class_id).delete()
    db_sess.query(Subject).filter(Subject.class_id == class_id).delete()
    db_sess.query(Schedule).filter(Schedule.class_id == class_id).delete()
    db_sess.commit()
    db_sess.close()
    return redirect('/profile')
