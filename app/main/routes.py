from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Major, ResearchTopic, Language
from app.main.models import Student
#from app.main.forms import CourseForm, EditForm, EmptyForm
from app.student.forms import SortForm
from flask_login import current_user, login_required
from sqlalchemy import text
from wtforms.validators import DataRequired, Email
from datetime import datetime


from app.main import main_blueprint as main

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SortForm()

    majors = db.session.scalars(sqla.select(Major)).all()
    form.majors.choices = [('', 'Select Major')] + [(m.id, m.name) for m in majors]

    courses = db.session.scalars(sqla.select(Course)).all()
    form.courses.choices = [('', 'Select Course')] + [(c.id, c.name) for c in courses]

    instructors = db.session.scalars(sqla.select(Faculty)).all()
    form.course_instructors.choices = [('', 'Instructor')] + [(i.id, f"{i.firstname} {i.lastname or ''}".strip()) for i in instructors]

    topics = db.session.scalars(sqla.select(ResearchTopic).distinct()).all()
    form.research_topics.choices = [('', 'Topic')] + [(t.name, t.name) for t in topics]

    languages = db.session.scalars(sqla.select(Language).distinct()).all()
    form.languages.choices = [('', 'Language')] + [(l.name, l.name) for l in languages]

    Positions = sqla.select(Position)
    if form.validate_on_submit(): 
        if form.majors.data:
            Positions = Positions.join(Position.majors).where(Major.id == form.majors.data)
        if form.courses.data:
            Positions = Positions.join(Position.courses).where(Position.id == form.courses.data)
        if form.grades.data:
            Positions = Positions.where(Position.min_gpa >= float(form.grades.data))
        if form.course_instructors.data:
            Positions = Positions.join(Position.faculty).where(Faculty.id == form.course_instructors.data)
        if form.research_topics.data:
            Positions = Positions.join(Position.research_topics).where(ResearchTopic.id == form.research_topics.data)
        if form.languages.data:
            Positions = Positions.join(Position.languages).where(Language.id == form.languages.data)

    Students = db.session.scalars(sqla.select(Student))
    PositionsA = db.session.scalars(Positions).all()
    return render_template('student_index.html', title="Course List", students = Students, form = form, positions=PositionsA)

@main.route('/faculty', methods=['GET'])
@main.route('/faculty_index', methods=['GET'])
@login_required
def faculty_index():
    #courses = db.session.scalars(sqla.select(Course))
    FacultyList = db.session.scalars(sqla.select(Faculty))
    Positions = db.session.scalars(sqla.select(Position))
    return render_template('faculty_index.html', title="Course List", faculty = FacultyList, positions=Positions)

@main.route('/position/<position_id>/view', methods=['GET'])
@login_required
def view_position(position_id):
    position=Position.query.get_or_404(position_id)
    return render_template('position_detail_page.html',position=position)

