from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Application
from app.main.models import Student
#from app.main.forms import CourseForm, EditForm, EmptyForm
from flask_login import current_user, login_required
from sqlalchemy import text

from app.main import main_blueprint as main

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    #courses = db.session.scalars(sqla.select(Course))
    Students = db.session.scalars(sqla.select(Student))
    return redirect(url_for('student.student_profile_view', student_id = current_user.id))

@main.route('/position/<position_id>/view', methods=['GET'])
@login_required
def view_position(position_id):
    position=Position.query.get_or_404(position_id)
    return render_template('position_detail.html',position=position)
