from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

#from app.main.models import Course, Student, Major
from app.main.models import Student
#from app.main.forms import CourseForm, EditForm, EmptyForm
from flask_login import current_user, login_required
from sqlalchemy import text

from app.main import main_blueprint as main

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    empty_form = EmptyForm()
    #courses = db.session.scalars(sqla.select(Course))
    Students = db.session.scalars(sqla.select(Student))
    return render_template('student.index.html', title="Course List", students = Students, form = empty_form)