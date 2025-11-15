from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import  ValidationError, DataRequired   
from wtforms import TextAreaField            
from wtforms.validators import Length 

from app import db
import sqlalchemy as sqla
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from app.main.models import Major, Course

class SortForm(FlaskForm):
    majors = SelectField('Sort By', choices=[('date','Date'), ('title', 'Title'), ('likes', '# of likes'), ('happiness', 'Happiness level')], default='date')
    courses = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    grades = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    course_instructors = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    research_topics = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    languages = SelectField('Sort By', choices=[('',''), ('', ''), ('', ''), ('', '')], default='')
    Refresh = SubmitField('Refresh')

