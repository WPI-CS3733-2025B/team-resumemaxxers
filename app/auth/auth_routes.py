from app import db
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla

from app.main.models import Student, CourseEnrollment, Faculty, Course
from app.auth.auth_forms import RegistrationForm, LoginForm, RegistrationFormFaculty
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth


@auth.route('/student/register', methods=['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        student = Student(username=rform.username.data,
                          firstname=rform.firstname.data,
                          lastname=rform.lastname.data,
                          email=rform.email.data,
                          majors=rform.majors.data,
                          gpa=rform.gpa.data,
                          research_topics=rform.research_topics.data,
                          languages=rform.languages.data
                          )

        for entry in rform.courses.entries:
            db.session.add(
                CourseEnrollment(
                    student=student,
                    course=entry.form.course.data,
                    instructor=entry.form.instructor.data,
                    grade=entry.form.grade.data
                )
            )

        student.set_password(rform.password.data)
        db.session.add(student)
        db.session.commit()

        login_user(student, remember=True)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=rform, Course=Course, Faculty=Faculty)


@auth.route('/faculty/login', methods = ['GET', 'POST'])
def register_faculty():
    rform = RegistrationFormFaculty()
    if rform.validate_on_submit():
        query = sqla.select(Faculty).where(Faculty.username == rform.username.data)
        fac = db.session.scalars(query).first()

        if (fac is None) or (fac.check_password(rform.password.data) == False):
            return redirect(url_for('auth.register_faculty'))

        login_user(fac, remember=True)
        flash('The user {} has successfully logged in!'.format(current_user.username))
        return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))
    return render_template('register_faculty.html', form = rform)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == "student":
            return redirect(url_for('main.index', student_id=current_user.id))
        else:
            return redirect(url_for('faculty.faculty_index', faculty_id=current_user.id))

    lform = LoginForm()

    if lform.validate_on_submit():

        user_role = lform.role.data
        username = lform.username.data
        password = lform.password.data
        remember_me = lform.remember_me.data

        user = None
        if user_role == 'student':
            query = sqla.select(Student).where(Student.username == username)
            user = db.session.scalars(query).first()
            if user and user.check_password(password):
                login_user(user, remember=remember_me)
                flash('The user {} has successfully logged in!'.format(user.username))
                return redirect(url_for('student.student_index', student_id=user.id))
        elif user_role == 'faculty':
            query = sqla.select(Faculty).where(Faculty.username == username)
            user = db.session.scalars(query).first()
            if user and user.check_password(password):
                login_user(user, remember=remember_me)
                flash('The user {} has successfully logged in!'.format(user.username))
                return redirect(url_for('faculty.faculty_index', faculty_id=user.id))

        flash('Invalid username, password or role selection.')
        return redirect(url_for('auth.login'))
    return render_template('login.html', form=lform)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# @auth.route('/faculty/verify/<token>', methods = ['GET'])
# @auth.route('/faculty/login/sso', methods = ['GET'])