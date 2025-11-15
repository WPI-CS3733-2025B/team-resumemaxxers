from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Application, Recommendation
from app.main.models import Student
from app.main.forms import ApplyPositionForm
from flask_login import current_user, login_required
from sqlalchemy import text
from wtforms.validators import DataRequired, Email


from app.main import main_blueprint as main

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    empty_form = EmptyForm()
    #courses = db.session.scalars(sqla.select(Course))
    Students = db.session.scalars(sqla.select(Student))
    return render_template('student.index.html', title="Course List", students = Students, form = empty_form)

@main.route('/position/<position_id>/view', methods=['GET'])
@login_required
def view_position(position_id):
    position=Position.query.get_or_404(position_id)
    return render_template('position_detail.html',position=position)

@main.route('/position/<position_id>/apply', methods=['GET', 'POST'])
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
