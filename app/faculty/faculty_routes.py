from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla
from datetime import datetime

from app.faculty.faculty_forms import *
from app.main.models import Course, Student, Position, Faculty, Application
from app.main.models import Faculty
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
        return redirect(url_for('faculty.index'))

    return render_template('faculty_profile.html', title=f"{faculty_user.firstname}'s Profile", user=faculty_user)

@faculty.route('/faculty/<faculty_id>/index', methods=['GET'])
@login_required
def faculty_index(faculty_id):
    faculty_user = db.session.get(Faculty, faculty_id)
    if faculty_user is None:
        flash('Faculty not found.', 'error')
        return redirect(url_for('faculty.index'))

    Positions = db.session.scalars(sqla.select(Position))
    return render_template('faculty_index.html', title=f"{faculty_user.firstname}'s Dashboard", user=faculty_user, positions=Positions  )

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
        new_position = Position(
            name=cform.name.data,
            description=cform.description.data,
            start_date=datetime.strptime(str(cform.start_date.data), '%Y-%m-%d').date(),
            end_date=datetime.strptime(str(cform.end_date.data), '%Y-%m-%d').date(),
            team_size=int(cform.team_size.data),
            min_gpa=float(cform.min_gpa.data),
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