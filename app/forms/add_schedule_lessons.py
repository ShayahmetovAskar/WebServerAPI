from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


# Поле выбора урока (из предложенного списка)
class SubjectForm(FlaskForm):
    name_ = SelectField('', validators=[DataRequired()])

    class Meta:
        csrf = False


# Поле с группой полей выборов урока
class DayScheduleForm(FlaskForm):
    subjects = FieldList(FormField(SubjectForm), min_entries=0)

    class Meta:
        csrf = False


# Поле с группой групп полей выборов уроков
class WeekScheduleForm(FlaskForm):
    days = FieldList(FormField(DayScheduleForm), min_entries=7)
    submit = SubmitField('Подтвердить')
