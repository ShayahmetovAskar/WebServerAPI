from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AddLessonForm(FlaskForm):
    lesson = SelectField('Предмет', validators=[DataRequired()])
    homework = TextAreaField('Домашнее задание')
    submit = SubmitField('Продолжить')
