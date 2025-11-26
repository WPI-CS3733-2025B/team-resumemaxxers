from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla
from datetime import datetime

from app.faculty.faculty_forms import *
from app.main.models import Course, Student, Position, Faculty, Application, Recommendation
from app.main.models import Faculty
from app.email import send_email
#from app.main.forms import CourseForm, EditForm, EmptyForm
from app.auth.auth_forms import EditProfileForm
from flask_login import current_user, login_required
from sqlalchemy import text

from app.main import main_blueprint as main
from app.faculty import faculty_blueprint as faculty

@faculty.route('/faculty/<faculty_id>/profile/view', methods=['GET'])
@login_required
def faculty_profile_view(faculty_id):
    faculty_user = db.session.get(Faculty, faculty_id)
    if faculty_user is None:
        flash('Faculty not found.', 'error')
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))

    return render_template('faculty_profile.html', title=f"{faculty_user.firstname}'s Profile", user=faculty_user)

@faculty.route('/faculty/<application_id>/view', methods=['GET'])
@login_required
def view_application(application_id):
    application = db.session.get(Application, application_id)
    if application is None:
        flash('Application not found.', 'error')
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))
    
    return render_template('application_detail_page.html', application=application)


@faculty.route('/faculty/<application_id>/approve', methods=['GET'])
@login_required
def student_approve(application_id):
    application = db.session.get(Application, application_id)
    if application is None:
        flash('Application not found.', 'error')
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))
    application.status = "approved"
    db.session.commit()
    # Send a notification email to the student
    subject = f"{application.position.name} - approved"
    message = f"""
            Greetings, {application.student.username}!

            Get excited! Your application for the role {application.position.name} has been approved!

            May your research be epic.

            Best wishes,
            Matvei "G-Chist" Shestopalov
            Head of Vibe Coding | Research App Development Team
            """

    send_email(application.student.email, subject, message)
    flash("Student approved :)")
    return redirect(request.referrer or url_for('faculty.faculty_dashboard'))

@faculty.route('/faculty/<application_id>/reject', methods=['GET'])
@login_required
def student_reject(application_id):
    application = db.session.get(Application, application_id)
    if application is None:
        flash('Application not found.', 'error')
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))
    application.status = "rejected"
    db.session.commit()
    # Send a notification email to the student
    subject = f"{application.position.name} - rejected"
    message = f"""
            Greetings, {application.student.username}!

            We are sorry to inform you that your application for the role {application.position.name} has been rejected.

            May your research be epic.

            Best wishes,
            Matvei "G-Chist" Shestopalov
            Head of Vibe Coding | Research App Development Team
            """

    send_email(application.student.email, subject, message)
    flash("Student rejected :(")
    return redirect(request.referrer or url_for('faculty.faculty_dashboard'))
               
@faculty.route('/faculty/recommendation/<recommendation_id>/approve', methods=['GET'])
@login_required
def recommendation_approve(recommendation_id):
    recommendation = db.session.get(Recommendation, recommendation_id)
    if recommendation is None:
        flash('Recommendation not found.', 'error')
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))
    recommendation.status = "approved"
    db.session.commit()
    # Send a notification email to the student
    subject = f"{recommendation.application.position.name} - approved"
    message = f"""
            Greetings, {recommendation.student.username}!

            Get excited! Your application for the role {recommendation.application.position.name} has been approved!

            May your research be epic.

            Best wishes,
            Matvei "G-Chist" Shestopalov
            Head of Vibe Coding | Research App Development Team
            """

    send_email(recommendation.student.email, subject, message)
    flash("Student approved :)")
    return redirect(request.referrer or url_for('faculty.faculty_dashboard'))


@faculty.route('/faculty/recommendation/<recommendation_id>/reject', methods=['GET'])
@login_required
def recommendation_reject(recommendation_id):
    recommendation = db.session.get(Recommendation, recommendation_id)
    if recommendation is None:
        flash('Application not found.', 'error')
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))
    recommendation.status = "rejected"
    db.session.commit()
    # Send a notification email to the student
    subject = f"{recommendation.application.position.name} - rejected"
    message = f"""
            Greetings, {recommendation.application.student.username}!

            We are sorry to inform you that your application for the role {recommendation.application.position.name} has been rejected.

            May your research be epic.

            Best wishes,
            Matvei "G-Chist" Shestopalov
            Head of Vibe Coding | Research App Development Team
            """

    send_email(recommendation.student.email, subject, message)
    flash("Student rejected :(")
    return redirect(request.referrer or url_for('faculty.faculty_dashboard'))

@faculty.route('/faculty/<faculty_id>/index', methods=['GET'])
@login_required
def faculty_index(faculty_id):
    faculty_user = db.session.get(Faculty, faculty_id)
    if faculty_user is None:
        flash('Faculty not found.', 'error')
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))

    Positions = db.session.scalars(sqla.select(Position).where(Position.faculty_id == faculty_id)).all()
    Applications = db.session.scalars(sqla.select(Application).join(Position).where(Position.faculty_id == faculty_id)).all()
    return render_template('faculty_index.html', title=f"{faculty_user.firstname}'s Dashboard", user=faculty_user, positions=Positions, applications=Applications )

@faculty.route('/faculty/<faculty_id>/create_position', methods=['GET', 'POST'])
@login_required
def create_position(faculty_id):
    faculty_user = db.session.get(Faculty, faculty_id)
    if faculty_user is None:
        flash('Faculty not found.', 'error')
        return redirect(url_for('main.index'))

    if str(current_user.id) != str(faculty_id) or current_user.role != 'faculty':
        flash('You are not authorized to create positions for this faculty.', 'error')
        return redirect(url_for('main.index'))

    cform = CreatePosition()

    if cform.validate_on_submit():
        if cform.min_gpa.data:
                try:
                    the_gpa = float(cform.min_gpa.data)
                    if the_gpa > 5.0:
                        flash('GPA cannot be greater than 5.0.', 'error')
                        return redirect(url_for('faculty.create_position'))
                except ValueError:
                    flash('Invalid input for Minimum GPA. Please enter a valid number.', 'error')
                    return redirect(url_for('faculty.create_position'))
        new_position = Position(
            name=cform.name.data,
            description=cform.description.data,
            start_date=datetime.strptime(str(cform.start_date.data), '%Y-%m-%d').date(),
            end_date=datetime.strptime(str(cform.end_date.data), '%Y-%m-%d').date(),
            team_size=int(cform.team_size.data),
            min_gpa=the_gpa,
            ref_required=cform.ref_required.data,
            faculty_id=faculty_user.id
        )


        # Handle many-to-many relationships
        new_position.majors = cform.majors.data
        new_position.research_topics = cform.research_topics.data
        new_position.languages = cform.languages.data
        new_position.courses = cform.courses.data

        db.session.add(new_position)
        db.session.commit()
        flash('Position created successfully!', 'success')
        return redirect(url_for('faculty.faculty_index', faculty_id=faculty_user.id))

    else:
        for fieldName, errorMessages in cform.errors.items():
            for err in errorMessages:
                print(err)

    return render_template('create_position.html', title='Create Position', form=cform, user=faculty_user)


@faculty.route('/faculty/<position_id>/edit_position', methods=['GET', 'POST'])
@login_required
def edit_position(position_id):
    form = EditPositionForm()
    position=Position.query.get_or_404(position_id)
    if form.validate_on_submit():
        if form.min_gpa.data:
                try:
                    position.min_gpa = float(form.min_gpa.data)
                    if position.min_gpa > 5.0:
                        flash('GPA cannot be greater than 5.0.', 'error')
                        return redirect(url_for('faculty.edit_position'))
                except ValueError:
                    flash('Invalid input for Minimum GPA. Please enter a valid number.', 'error')
                    return redirect(url_for('faculty.edit_position'))
        position.name = form.name.data
        position.description = form.description.data
        position.start_date = form.start_date.data
        position.end_date = form.end_date.data
        position.team_size = form.team_size.data
        position.ref_required = form.ref_required.data
        position.faculty = form.faculty.data
        position.majors = form.majors.data
        position.research_topics = form.research_topics.data
        position.courses = form.courses.data
        position.languages = form.languages.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.view_position', position_id=position.id))
    elif request.method == 'GET':
        form.name.data = position.name
        form.description.data = position.description
        form.start_date.data = position.start_date
        form.end_date.data = position.end_date
        form.team_size.data = position.team_size
        form.min_gpa.data = position.min_gpa
        form.ref_required.data = position.ref_required
        form.faculty.data = position.faculty
        form.majors.data = position.majors
        form.research_topics.data = position.research_topics
        form.courses.data = position.courses
        form.languages.data = position.languages
    return render_template('edit_position.html', title='Edit Position', form=form, position=position)


@faculty.route('/faculty/<position_id>/delete_position', methods=['GET', 'POST'])
@login_required
def delete_position(position_id):
    position = Position.query.get_or_404(position_id)
    
    # Check authorization - only the faculty who created it can delete
    if current_user.role != 'faculty' or position.faculty_id != current_user.id:
        flash('You are not authorized to delete this position.', 'error')
        return redirect(url_for('faculty.faculty_index'))
    
    # Delete related applications first to maintain referential integrity
    Application.query.filter_by(position_id=position.id).delete()
    
    db.session.delete(position)
    db.session.commit()
    flash('Position deleted successfully!', 'success')
    return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))

@faculty.route('/faculty/dashboard', methods=['GET'])
@login_required
def faculty_dashboard():
    if not isinstance(current_user._get_current_object(), Faculty):
        flash("Only faculty can view the dashboard.")
        return redirect(url_for('faculty.faculty_index'))

    applications = db.session.scalars(sqla.select(Application).join(Position).where(Position.faculty_id == current_user.id))
    recommendations = db.session.scalars(sqla.select(Recommendation).join(Faculty).where(Faculty.id == current_user.id))
    
    return render_template('faculty_dashboard.html',
                           applications=applications,
                           recommendations=recommendations,
                           title="Faculty Dashboard")