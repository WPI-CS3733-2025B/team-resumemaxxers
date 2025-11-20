from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import Optional

from app.main.models import Course, Faculty

def course_query():
    return Course.query.order_by(Course.coursenum).all()

def instructor_query():
    return Faculty.query.order_by(Faculty.lastname).all()

class CourseEnrollmentForm(FlaskForm):
    course = QuerySelectField(
        'Course',
        query_factory=course_query,
        get_label=lambda c: f"{c.coursenum} – {c.name}",
        allow_blank=False
    )

    instructor = QuerySelectField(
        'Instructor',
        query_factory=instructor_query,
        get_label=lambda i: f"{i.lastname}, {i.firstname}",
        allow_blank=True
    )

    grade = StringField("Grade", validators=[Optional()])
