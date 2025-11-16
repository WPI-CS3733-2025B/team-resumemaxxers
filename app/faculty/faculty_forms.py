from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, PasswordField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email
from wtforms import TextAreaField            
from wtforms.validators import Length 

from app import db
import sqlalchemy as sqla
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from app.main.models import Major, Course, Faculty, ResearchTopic, Language


class CreatePosition(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    start_date = StringField('Start Date', validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    team_size = StringField('Team Size', validators=[DataRequired()])
    min_gpa = StringField('Minimum GPA', validators=[DataRequired()])
    ref_required = BooleanField('Reference Required')
    faculty = QuerySelectMultipleField('Faculty',
                                      query_factory=lambda: db.session.scalars(sqla.select().order_by(Faculty.username)),
                                      get_label=lambda theFaculty: theFaculty.username,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    majors = QuerySelectMultipleField('Majors',
                                      query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                      get_label=lambda theMajor: theMajor.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    research_topics = QuerySelectMultipleField('Research Topics',
                                      query_factory=lambda: db.session.scalars(sqla.select().order_by(ResearchTopic.name)),
                                      get_label=lambda theTopic: theTopic.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    courses = QuerySelectMultipleField('Courses',                       
                                      query_factory=lambda: db.session.scalars(sqla.select(Course).order_by(Course.title)),
                                      get_label=lambda theCourse: theCourse.title,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    languages = QuerySelectMultipleField('Languages',
                                      query_factory=lambda: db.session.scalars(sqla.select().order_by(Language.name)),
                                      get_label=lambda theLanguage: theLanguage.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())    
    submit = SubmitField('Edit')

