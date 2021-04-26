from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


# Форма для изменения / добавления класса
class ClassForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    key = PasswordField('Ключ для входа', validators=[DataRequired()])
    submit = SubmitField('Добавить')
