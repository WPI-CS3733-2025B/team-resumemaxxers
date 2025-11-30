from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, PasswordField, DateField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email
from wtforms import TextAreaField
from wtforms.validators import Length

from app import db
import sqlalchemy as sqla
from wtforms_sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from wtforms.widgets import ListWidget, CheckboxInput
from app.main.models import Major, Course, Faculty, ResearchTopic, Language


class CreatePosition(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], render_kw={"class": "datepicker-input"})
    end_date = DateField('End Date', validators=[DataRequired()], render_kw={"class": "datepicker-input"})
    team_size = StringField('Team Size', validators=[DataRequired()])
    min_gpa = StringField('Minimum GPA', validators=[DataRequired()])
    ref_required = BooleanField('Reference Required')
    majors = QuerySelectMultipleField('Majors',
                                      query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                      get_label=lambda theMajor: theMajor.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    research_topics = QuerySelectMultipleField('Research Topics',
                                      query_factory=lambda: db.session.scalars(sqla.select(ResearchTopic).order_by(ResearchTopic.name)),
                                      get_label=lambda theTopic: theTopic.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    courses = QuerySelectMultipleField('Courses',
                                      query_factory=lambda: db.session.scalars(sqla.select(Course).order_by(Course.name)),
                                      get_label=lambda theCourse: theCourse.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    languages = QuerySelectMultipleField('Languages',
                                      query_factory=lambda: db.session.scalars(sqla.select(Language).order_by(Language.name)),
                                      get_label=lambda theLanguage: theLanguage.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    submit = SubmitField('Create Position')


class EditPositionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], render_kw={"class": "datepicker-input"})
    end_date = DateField('End Date', validators=[DataRequired()], render_kw={"class": "datepicker-input"})
    team_size = StringField('Team Size', validators=[DataRequired()])
    min_gpa = StringField('Minimum GPA', validators=[DataRequired()])
    ref_required = BooleanField('Reference Required')
    faculty = QuerySelectField('Faculty',
                                      query_factory=lambda: db.session.scalars(sqla.select(Faculty).order_by(Faculty.username)),
                                      get_label=lambda theFaculty: theFaculty.username,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())    
    majors = QuerySelectMultipleField('Majors',
                                      query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                      get_label=lambda theMajor: theMajor.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    research_topics = QuerySelectMultipleField('Research Topics',
                                      query_factory=lambda: db.session.scalars(sqla.select(ResearchTopic).order_by(ResearchTopic.name)),
                                      get_label=lambda theTopic: theTopic.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    courses = QuerySelectMultipleField('Courses',
                                      query_factory=lambda: db.session.scalars(sqla.select(Course).order_by(Course.name)),
                                      get_label=lambda theCourse: theCourse.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    languages = QuerySelectMultipleField('Languages',
                                      query_factory=lambda: db.session.scalars(sqla.select(Language).order_by(Language.name)),
                                      get_label=lambda theLanguage: theLanguage.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    submit = SubmitField('Submit Changes')

class AddCourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    coursenum = StringField('Course Number', validators=[DataRequired()])
    majors = QuerySelectMultipleField('Majors',
                                      query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                      get_label=lambda theMajor: theMajor.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    submit = SubmitField('Add course')
    
class AddResearchForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add research topic')

class AddMajorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add major')

class AddLanguageForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add language')

class DeleteCourseForm(FlaskForm):
    courses = QuerySelectMultipleField('Courses',
                                      query_factory=lambda: db.session.scalars(sqla.select(Course).order_by(Course.name)),
                                      get_label=lambda theCourse: theCourse.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    submit = SubmitField('Delete course')


class DeleteResearchForm(FlaskForm):
    research_topics = QuerySelectMultipleField('Research Topics',
                                      query_factory=lambda: db.session.scalars(sqla.select(ResearchTopic).order_by(ResearchTopic.name)),
                                      get_label=lambda theTopic: theTopic.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    submit = SubmitField('Delete research topic')

    
class DeleteMajorForm(FlaskForm):
    majors = QuerySelectMultipleField('Majors',
                                      query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                      get_label=lambda theMajor: theMajor.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    submit = SubmitField('Delete major')

class DeleteLanguageForm(FlaskForm):
    languages = QuerySelectMultipleField('Languages',
                                      query_factory=lambda: db.session.scalars(sqla.select(Language).order_by(Language.name)),
                                      get_label=lambda theLanguage: theLanguage.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    submit = SubmitField('Delete language')
