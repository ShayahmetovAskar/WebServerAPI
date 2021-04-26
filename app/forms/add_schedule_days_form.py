from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange, ValidationError


# Форма для определения количества уроков для каждого дня недели
class AddScheduleDaysForm(FlaskForm):
    mon = IntegerField('Количество уроков в понедельник',
                       validators=[InputRequired(), NumberRange(min=0, max=50)])
    tue = IntegerField('Количество уроков во вторник',
                       validators=[InputRequired(), NumberRange(min=0, max=50)])
    wed = IntegerField('Количество уроков в среду',
                       validators=[InputRequired(), NumberRange(min=0, max=50)])
    thu = IntegerField('Количество уроков в четверг',
                       validators=[InputRequired(), NumberRange(min=0, max=50)])
    fri = IntegerField('Количество уроков в пятницу',
                       validators=[InputRequired(), NumberRange(min=0, max=50)])
    sat = IntegerField('Количество уроков в субботу',
                       validators=[InputRequired(), NumberRange(min=0, max=50)])

    submit = SubmitField('Продолжить')
