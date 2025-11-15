from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

from app import db
from app.main.models import *
import sqlalchemy as sqla


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    firstname = StringField('First Name', validators = [DataRequired()])
    lastname = StringField('Last Name', validators = [DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    id = StringField('Address', validators = [DataRequired()])

    majors = QuerySelectMultipleField('Majors',
                                      query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                      get_label=lambda theMajor: theMajor.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())

    gpa = StringField('GPA', validators = [DataRequired()])

    research_topics = QuerySelectMultipleField('Interests',
                                      query_factory=lambda: db.session.scalars(sqla.select(ResearchTopic).order_by(ResearchTopic.name)),
                                      get_label=lambda theResearchTopic: theResearchTopic.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())

    languages = QuerySelectMultipleField('Languages',
                                               query_factory=lambda: db.session.scalars(
                                                   sqla.select(Language).order_by(Language.name)),
                                               get_label=lambda theLanguage: theLanguage.name,
                                               widget=ListWidget(prefix_label=False),
                                               option_widget=CheckboxInput())

    courses = QuerySelectMultipleField('Courses Taken',
                                               query_factory=lambda: db.session.scalars(
                                                   sqla.select(Course).order_by(Course.name)),
                                               get_label=lambda theCourse: theCourse.name,
                                               widget=ListWidget(prefix_label=False),
                                               option_widget=CheckboxInput())

    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Post')

    def validate_username(self, username):
        query = sqla.select(Student).where(Student.username == username.data)
        student = db.session.scalars(query).first()
        if student is not None: 
            raise ValidationError('The username already exists! Please use a different username.')
     
    def validate_email(self, email):
        query = sqla.select(Student).where(Student.email == email.data)
        student = db.session.scalars(query).first()
        if student is not None: 
            raise ValidationError('The username already exists! Please use a different email.')
                                  
class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

