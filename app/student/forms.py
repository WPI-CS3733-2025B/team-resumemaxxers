from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, PasswordField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email
from wtforms import TextAreaField            
from wtforms.validators import Length, Optional

from app import db
import sqlalchemy as sqla
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from app.main.models import Major, Course

class SortForm(FlaskForm):
    majors = SelectField('Sort By', choices=[('date','OptionA'), ('title', 'OptionB'), ('likes', 'OptionC'), ('happiness', 'OptionD')], default='date')
    courses = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    grades = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    course_instructors = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    research_topics = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    languages = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    Refresh = SubmitField('Refresh')

class EditForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', validators=[Length(min=0, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    majors = QuerySelectMultipleField('Majors',
                                      query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                      get_label=lambda theMajor: theMajor.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())

    submit = SubmitField('Edit')

class ApplyPositionForm(FlaskForm):
    statement = TextAreaField("Short statement",
        validators=[
            DataRequired(message="Please enter your short statement."),
            Length(min=10, max=1500, message="Statement must be between 10 and 1500 characters.")
        ]
    )

    reference_email = StringField("Reference Email (if required)", validators=[Optional(), Email(message="Invalid email format.")])

    submit = SubmitField("Apply")