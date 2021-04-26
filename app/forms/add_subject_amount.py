from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired


# Поле определения количества уроков для заполнения таблицы предметов класса
class AddSubjectsAmount(FlaskForm):
    amount = IntegerField('Количество предметов', validators=[InputRequired()])
    submit = SubmitField('Далее')
