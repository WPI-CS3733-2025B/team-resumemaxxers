from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Course, Student, Position, Faculty, Application
from app.main.models import Faculty
#from app.main.forms import CourseForm, EditForm, EmptyForm
from app.auth.auth_forms import EditProfileForm
from flask_login import current_user, login_required
from sqlalchemy import text

from app.main import main_blueprint as main
from app.faculty import faculty_blueprint as faculty

@faculty.route('/faculty/<faculty_id>/profile/view', methods=['GET'])
def faculty_profile_view(faculty_id):
    faculty = db.session.get(Faculty, faculty_id)
    if faculty is None:
        flash('Faculty not found.', 'error')
        return redirect(url_for('faculty.index')) # Redirect to a suitable page, e.g., main index

    return render_template('faculty_profile.html', title=f"{faculty.firstname}'s Profile", user=faculty)

@faculty.route('/faculty/<faculty_id>/index', methods=['GET'])
def faculty_index(faculty_id):
    faculty = db.session.get(Faculty, faculty_id)
    if faculty is None:
        flash('Faculty not found.', 'error')
        return redirect(url_for('main.index')) # Redirect to a suitable page, e.g., main index

    return render_template('faculty_index.html', title=f"{faculty.firstname}'s Dashboard", user=faculty)