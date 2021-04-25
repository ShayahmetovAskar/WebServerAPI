import os
import secrets
from PIL import Image

from flask import Blueprint, render_template, request, url_for, flash, redirect
from flask_login import current_user, login_required

from app.data import db_session
from app.data.classes import Class
from app.data.users import User
from app.forms.update_account_form import UpdateAccountData

index = Blueprint('index', __name__, static_folder='static',
                  template_folder='templates')


def save_picture(form_picture):
    from app import root_path
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(root_path, 'static/img/profile_pictures', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@index.route('/')
def test():
    return render_template('base.html')


@index.route('/profile/')
@login_required
def profile():
    db_sess = db_session.create_session()
    current_user_ = db_sess.query(User).filter(User.id == current_user.id).first()
    classes = [{'id': i.id, 'name': i.name} for i in current_user_.member_of]
    db_sess.close()
    image_file = url_for('static', filename='img/profile_pictures/' + current_user.image_file)
    return render_template('profile.html', image_file=image_file, classes=classes)


@index.route('/update_user_data', methods=['GET', 'POST'])
@login_required
def update_user_data():
    form = UpdateAccountData()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        db_sess.merge(current_user)
        db_sess.commit()
        db_sess.close()
        return redirect('/profile')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.surname.data = current_user.surname

    return render_template('edit_user_data.html', form=form)
