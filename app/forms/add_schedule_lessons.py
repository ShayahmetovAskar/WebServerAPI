from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SubjectForm(FlaskForm):
    name_ = SelectField('', validators=[DataRequired()])

    class Meta:
        csrf = False


class DayScheduleForm(FlaskForm):
    subjects = FieldList(FormField(SubjectForm), min_entries=0)

    class Meta:
        csrf = False


class WeekScheduleForm(FlaskForm):
    days = FieldList(FormField(DayScheduleForm), min_entries=7)
    submit = SubmitField('Подтвердить')
