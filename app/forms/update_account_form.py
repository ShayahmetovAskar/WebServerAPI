from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Форма для обновления полей аккаунта
class UpdateAccountData(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    name = StringField('Имя (Необязательно)')
    surname = StringField('Фамилия (Необязательно)')
    picture = FileField('Добавить фотографию', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Обновить')
