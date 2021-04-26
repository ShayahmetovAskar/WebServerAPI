from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


# Форма для изменения / добавления урока в дневнике
class AddLessonForm(FlaskForm):
    lesson = SelectField('Предмет', validators=[DataRequired()])
    homework = TextAreaField('Домашнее задание')
    submit = SubmitField('Продолжить')
