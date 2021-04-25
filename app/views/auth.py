from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user

from ..forms.login_form import LoginForm
from ..forms.signup_form import SignUpForm
from ..data import db_session
from ..data.users import User

auth = Blueprint('auth', __name__, static_folder='static',
                 template_folder='templates')


@auth.route('/login')
def login():
    form = LoginForm()
    return render_template('auth/login.html', form=form)


@auth.route('/login', methods=['POST'])
def login_post():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == request.form.get('email')).first()
    db_sess.close()
    if user and user.check_password(request.form.get('password')):
        login_user(user, remember=request.form.get('remember_me'))
        return redirect('/profile')
    form = LoginForm()
    return render_template('auth/login.html', message='Неправильный логин или пароль', form=form)


@auth.route('/signup')
def signup():
    form = SignUpForm()
    return render_template('auth/signup.html', form=form)


@auth.route('/signup', methods=['POST'])
def signup_post():
    form = SignUpForm()
    if request.form.get('password') != request.form.get('password_again'):
        return render_template('auth/signup.html', form=form, message='Пароли не совпадают')
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.email == request.form.get('email')).first():
        db_sess.close()
        return render_template('auth/signup.html', form=form,
                               message='Этот адрес почты уже используется')
    elif db_sess.query(User).filter(User.username == request.form.get('username')).first():
        db_sess.close()
        return render_template('auth/signup.html', form=form,
                               message='Это имя пользователя занято. Попробуйте другое')
    user = User(
        email=request.form.get('email'),
        username=request.form.get('username')
    )
    user.set_password(request.form.get('password'))
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()
    return redirect('/login')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect('/login')
