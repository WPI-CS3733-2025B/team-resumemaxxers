from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import *
from app.student.forms import ApplyPositionForm, SortForm
from app.auth.auth_forms import EditProfileForm
from flask_login import current_user, login_required
from sqlalchemy import text
from wtforms.validators import DataRequired, Email, Length, Optional


from app.main import main_blueprint as main
from app.student import student_blueprint as student


@student.route('/student/<student_id>/index', methods=['GET', 'POST'])
@login_required
def student_index(student_id):
        form = SortForm()

        majors = db.session.scalars(sqla.select(Major)).all()
        form.majors.choices = [(m.id, m.name) for m in majors]

        courses = db.session.scalars(sqla.select(Course)).all()
        form.courses.choices = [('', 'Select Course')] + [(c.id, c.name) for c in courses]

        instructors = db.session.scalars(sqla.select(Faculty)).all()
        form.course_instructors.choices = [('', 'Instructor')] + [(i.id, f"{i.firstname} {i.lastname or ''}".strip())
                                                                  for i in instructors]

        topics = db.session.scalars(sqla.select(ResearchTopic).distinct()).all()
        form.research_topics.choices = [('', 'Topic')] + [(t.name, t.name) for t in topics]

        languages = db.session.scalars(sqla.select(Language).distinct()).all()
        form.languages.choices = [('', 'Language')] + [(l.name, l.name) for l in languages]

        Positions = sqla.select(Position)
        if form.validate_on_submit():
            if form.majors.data and len(form.majors.data) > 0:
                Positions = Positions.join(Position.majors).where(Major.id.in_(form.majors.data)).distinct()
            if form.courses.data:
                Positions = Positions.join(Position.courses).where(Position.id == form.courses.data)
            if form.grades.data:
                Positions = Positions.where(Position.min_gpa >= float(form.grades.data))
            if form.course_instructors.data:
                Positions = Positions.join(Position.faculty).where(Faculty.id == form.course_instructors.data)
            if form.research_topics.data:
                Positions = Positions.join(Position.research_topics).where(
                    ResearchTopic.name == form.research_topics.data)
            if form.languages.data:
                Positions = Positions.join(Position.languages).where(Language.name == form.languages.data)

        Students = db.session.scalars(sqla.select(Student))
        PositionsA = db.session.scalars(Positions).all()
        return render_template('student_index.html', title="Course List", students=Students, form=form,
                               positions=PositionsA)

@student.route('/student/<student_id>/profile/view', methods=['GET'])
@login_required
def student_profile_view(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        flash('Student not found.', 'error')
        return redirect(url_for('main.index'))

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

        # Remove all existing records
        for enrollment in current_user.courses:
            db.session.delete(enrollment)

        # Re-add all from submitted form
        for entry in form.courses.entries:
            db.session.add(
                CourseEnrollment(
                    student=current_user,
                    course=entry.form.course.data,
                    instructor=entry.form.instructor.data,
                    grade=entry.form.grade.data
                )
            )

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('student.student_profile_view', student_id=current_user.id))

    elif request.method == "GET":
        # prepopulate simple fields
        form.username.data = current_user.username
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email
        form.majors.data = current_user.majors
        form.gpa.data = current_user.gpa
        form.research_topics.data = current_user.research_topics
        form.languages.data = current_user.languages

        # prepopulate list
        form.courses.entries = []
        for enrollment in current_user.courses:
            sub = {}
            sub['course'] = enrollment.course
            sub['instructor'] = enrollment.instructor
            sub['grade'] = enrollment.grade

            form.courses.append_entry(sub)

    return render_template('edit_profile.html', title='Edit Profile',
                           form=form, Course=Course, Faculty=Faculty)

@student.route('/position/<position_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_position(position_id):

    position=Position.query.get_or_404(position_id)

    existing_application = Application.query.filter_by(student_id=current_user.id, position_id=position.id).first()
    if existing_application:
        flash('You have already applied for this position.', 'error')
        return redirect(url_for('main.view_position', position_id=position.id))

    form = ApplyPositionForm()

    if position.ref_required:
        form.reference_email.validators = [DataRequired(message="Reference email is required."),
                                           Email(message="Invalid email address.")]

    if form.validate_on_submit():

        statement = form.statement.data
        reference_email = form.reference_email.data.strip() if form.reference_email.data else None

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

@main.route('/recommended')
@login_required
def recommended():
    if not isinstance(current_user._get_current_object(), Student):
        flash("Only students can view recommended positions.")
        return redirect(url_for('main.index'))

    try:
        # Get all positions for comparison
        all_positions = Position.query.all()
        print(f"\nDEBUG: Total positions in database: {len(all_positions)}")
        print(f"DEBUG: Student GPA: {current_user.gpa}")
        print(f"DEBUG: Student majors: {[m.name for m in current_user.majors]}")
        print(f"DEBUG: Student research topics: {[t.name for t in current_user.research_topics]}")
        
        for pos in all_positions:
            print(f"\nPosition: {pos.name}")
            print(f"  - Min GPA: {pos.min_gpa}")
            print(f"  - Majors: {[m.name for m in pos.majors]}")
            print(f"  - Research Topics: {[t.name for t in pos.research_topics]}")
        
        positions = current_user.recommended_positions()
        print(f"\nDEBUG: Found {len(positions)} recommended positions for student {current_user.username}")
        
        flash(f"Found {len(positions)} recommended positions out of {len(all_positions)} total positions.", "info")
    except Exception as e:
        print(f"ERROR in recommended_positions: {e}")
        import traceback
        traceback.print_exc()
        flash(f"Error getting recommendations: {str(e)}", "error")
        positions = []
    
    return render_template('recommended_positions.html',
                           positions=positions,
                           title="Recommended Positions")

@student.route('/student/dashboard', methods=['GET'])
@login_required
def student_dashboard():
    if not isinstance(current_user._get_current_object(), Student):
        flash("Only students can view the dashboard.")
        return redirect(url_for('main.index'))

    applications = current_user.applications
    recommendations = current_user.recommendations

    return render_template('student_dashboard.html',
                           applications=applications,
                           recommendations=recommendations,
                           title="Student Dashboard")
