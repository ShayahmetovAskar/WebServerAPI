from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired


# Форма для вступления в класс
class JoinClassForm(FlaskForm):
    key = PasswordField('Ключ', validators=[DataRequired()])
    submit = SubmitField('Продолжить')
