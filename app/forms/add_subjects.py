from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SubmitField
from wtforms.validators import DataRequired


class SubjectForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])

    class Meta:
        csrf = False


class SubjectsForm(FlaskForm):
    subjects = FieldList(FormField(SubjectForm), min_entries=0, validators=[DataRequired()])
    submit = SubmitField('Добавить')
