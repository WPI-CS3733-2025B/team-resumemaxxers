from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Application, Recommendation
from app.main.models import Student
from app.student.forms import ApplyPositionForm, SortForm
from app.auth.auth_forms import EditProfileForm
from flask_login import current_user, login_required
from sqlalchemy import text
from wtforms.validators import DataRequired, Email, Length, Optional


from app.main import main_blueprint as main
from app.student import student_blueprint as student

@student.route('/student/<student_id>/index', methods=['GET'])
@login_required
def student_index(student_id):
    return redirect(url_for('main.index'))

@student.route('/student/<student_id>/profile/view', methods=['GET'])
@login_required
def student_profile_view(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        flash('Student not found.', 'error')
        return redirect(url_for('student.index')) # Redirect to a suitable page, e.g., main index

    return render_template('student_profile.html', title=f"{student.firstname}'s Profile", user=student)


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

@student.route('/position/<position_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_position(position_id):
    position=Position.query.get_or_404(position_id)

    form = ApplyPositionForm()

    if position.ref_required:
        form.reference_email.validators = [DataRequired(message="Reference email is required."),
                                           Email(message="Invalid email address.")]

    if form.validate_on_submit():
        statement = form.statement.data
        reference_email = form.reference_email.data.strip()

        faculty_ref = None
        if reference_email:
            faculty_ref = Faculty.query.filter_by(email=reference_email).first()
            if not faculty_ref:
                flash("No faculty with this email found.")
                return render_template('apply_position.html', position=position, form=form)

        application = Application(
            student_id=current_user.id,
            position_id=position.id,
            statement=statement
        )
        db.session.add(application)
        db.session.commit()

        if faculty_ref:
            recommendation = Recommendation(
                student_id=current_user.id,
                faculty_id=faculty_ref.id,
                application_id=application.id
            )
            db.session.add(recommendation)
            db.session.commit()

        flash("Application submitted successfully!")
        return redirect(url_for('main.view_position', position_id=position.id))

    return render_template('apply_position.html', position=position, form=form)