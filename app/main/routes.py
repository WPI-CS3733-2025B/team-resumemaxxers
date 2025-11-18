from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Application, Recommendation
from app.main.models import Student
#from app.main.forms import CourseForm, EditForm, EmptyForm
from app.student.forms import SortForm
from flask_login import current_user, login_required
from sqlalchemy import text
from wtforms.validators import DataRequired, Email


from app.main import main_blueprint as main

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    form = SortForm()
    #courses = db.session.scalars(sqla.select(Course))
    Students = db.session.scalars(sqla.select(Student))
    Positions = db.session.scalars(sqla.select(Position))
    return render_template('student_index.html', title="Course List", students = Students, form = form, positions=Positions)

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
    return render_template('position_detail.html',position=position)

