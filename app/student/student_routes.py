from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Application
from app.main.models import Student
#from app.main.forms import CourseForm, EditForm, EmptyForm
from flask_login import current_user, login_required
from sqlalchemy import text

from app.main import main_blueprint as main
from app.student import student_blueprint as student

@student.route('/student/<student_id>/profile/view', methods=['GET'])
def student_profile_view(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        flash('Student not found.', 'error')
        return redirect(url_for('main.index')) # Redirect to a suitable page, e.g., main index

    return render_template('student_profile.html', title=f"{student.firstname}'s Profile", user=student)