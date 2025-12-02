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
from app.auth.role_required import role_required

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SortForm()

    majors = db.session.scalars(sqla.select(Major)).all()
    form.majors.choices = [(m.id, m.name) for m in majors]

    courses = db.session.scalars(sqla.select(Course)).all()
    form.courses.choices = [(c.id, c.name) for c in courses]

    instructors = db.session.scalars(sqla.select(Faculty)).all()
    form.course_instructors.choices = [(i.id, f"{i.firstname} {i.lastname or ''}".strip()) for i in instructors]

    topics = db.session.scalars(sqla.select(ResearchTopic).distinct()).all()
    form.research_topics.choices = [(t.name, t.name) for t in topics]

    languages = db.session.scalars(sqla.select(Language).distinct()).all()
    form.languages.choices = [(l.name, l.name) for l in languages]

    Positions = sqla.select(Position)
    if form.validate_on_submit(): 
        if form.majors.data and len(form.majors.data) > 0:
            Positions = Positions.join(Position.majors).where(Major.id.in_(form.majors.data)).distinct()
        if form.courses.data and len(form.courses.data) > 0:
            Positions = Positions.join(Position.courses).where(Course.id.in_(form.courses.data)).distinct()
        if form.grades.data:
            Positions = Positions.where(Position.min_gpa >= float(form.grades.data))
        if form.course_instructors.data:
            Positions = Positions.join(Position.faculty).where(Faculty.id == form.course_instructors.data).distinct()
        if form.research_topics.data and len(form.research_topics.data) > 0:
            Positions = Positions.join(Position.research_topics).where(ResearchTopic.name.in_(form.research_topics.data)).distinct()
        if form.languages.data and len(form.languages.data) > 0:
            Positions = Positions.join(Position.languages).where(Language.name.in_(form.languages.data)).distinct()

    Students = db.session.scalars(sqla.select(Student))
    Faculties = db.session.scalars(sqla.select(Faculty))
    PositionsA = db.session.scalars(Positions).all()
    if current_user.is_authenticated:
        if current_user.role == 'faculty':
            return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))
        elif current_user.role == 'student':
            return redirect(url_for('student.student_index', student_id=current_user.id))
    return render_template('student_index.html', title="Course List", students = Students, form = form, positions=PositionsA)

@main.route('/faculty', methods=['GET'])
@main.route('/faculty_index', methods=['GET'])
@login_required
@role_required("faculty")
def faculty_index():
    #courses = db.session.scalars(sqla.select(Course))
    FacultyList = db.session.scalars(sqla.select(Faculty))
    Positions = db.session.scalars(sqla.select(Position).order_by(Position.id.desc()))
    return render_template('faculty_index.html', title="Course List", faculty = FacultyList, positions=Positions)

@main.route('/position/<position_id>/view', methods=['GET'])
@login_required
def view_position(position_id):
    position=Position.query.get_or_404(position_id)
    # Prevent students from viewing full positions
    if current_user.role == 'student' and position.is_full():
        flash('This position is full and no longer accepting applications.', 'error')
        return redirect(url_for('student.student_index', student_id=current_user.id))
    return render_template('position_detail_page.html',position=position)


@main.route('/student_list/<position_id>/view', methods=['GET'])
@login_required
@role_required("faculty")
def view_student_list(position_id):  # TODO: IDEALLY MOVE THIS TO FACULTY ROUTES I GUESS...
    if isinstance(current_user, Faculty):  # if current user is faculty
        position=Position.query.get_or_404(position_id)
        return render_template('apply_student_list.html',position=position)
    else:
        return "Permission denied: you are not a faculty member"