from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Application
from app.main.models import Student
#from app.main.forms import CourseForm, EditForm, EmptyForm
from app.auth.auth_forms import EditProfileForm
from flask_login import current_user, login_required
from sqlalchemy import text

from app.main import main_blueprint as main
from app.student import student_blueprint as student

@student.route('/student/<student_id>/profile/view', methods=['GET'])
def student_profile_view(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        flash('Student not found.', 'error')
        return redirect(url_for('student.index')) # Redirect to a suitable page, e.g., main index

    return render_template('student_profile.html', title=f"{student.firstname}'s Profile", user=student)

@student.route('/faculty/<faculty_id>/profile/view', methods=['GET'])
def faculty_profile_view(faculty_id):
    faculty = db.session.get(Faculty, faculty_id)
    if faculty is None:
        flash('Faculty not found.', 'error')
        return redirect(url_for('faculty.index')) # Redirect to a suitable page, e.g., main index

    return render_template('faculty_profile.html', title=f"{faculty.firstname}'s Profile", user=faculty)

@student.route('/student/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.email = form.email.data
        current_user.majors = form.majors.data
        current_user.gpa = form.gpa.data
        current_user.research_topics = form.research_topics.data
        current_user.languages = form.languages.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('student.student_profile_view', student_id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email
        form.majors.data = current_user.majors
        form.gpa.data = current_user.gpa
        form.research_topics.data = current_user.research_topics
        form.languages.data = current_user.languages
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
