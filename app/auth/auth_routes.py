from app import db
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla

from app.main.models import Student, CourseEnrollment, Faculty, Course
from app.auth.auth_forms import RegistrationForm, LoginForm, RegistrationFormFaculty, VerificationForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth
from app.email import send_email
import hashlib


@auth.route('/auth/student/register', methods=['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        try:
            the_gpa = float(rform.gpa.data)
            if the_gpa > 5.0:
                flash('GPA cannot be greater than 5.0.', 'error')
                return render_template('register.html', form=rform, Course=Course, Faculty=Faculty)
        except ValueError:
            flash('Invalid input for Minimum GPA. Please enter a valid number.', 'error')
            return render_template('register.html', form=rform, Course=Course, Faculty=Faculty)
        student = Student(username=rform.username.data,
                          firstname=rform.firstname.data,
                          lastname=rform.lastname.data,
                          email=rform.email.data,
                          majors=rform.majors.data,
                          gpa=the_gpa,
                          research_topics=rform.research_topics.data,
                          languages=rform.languages.data
                          )

        # Email the user their verification code
        vercode_unhashed = student.email + "SALT!!!"
        subject = "Your Verification Code For Research App"
        message = f"""
        Greetings, {rform.username.data}!

        Please find your verification code below:

        **{hashlib.sha256(vercode_unhashed.encode('utf-8')).hexdigest()}**

        May your research be epic.

        Best wishes,
        Matvei "G-Chist" Shestopalov
        Head of Vibe Coding | Research App Development Team
        """

        send_email(rform.email.data, subject, message)

        for entry in rform.courses.entries:
            if entry.form.course.data and entry.form.instructor.data and entry.form.grade.data:
                db.session.add(
                    CourseEnrollment(
                        student=student,
                        course=entry.form.course.data,
                        instructor=entry.form.instructor.data,
                        grade=entry.form.grade.data
                    )
                )
            else: 
                flash('Please provide the course, instructor, and grade for each course entry.', 'error')
                return render_template('register.html', form=rform, Course=Course, Faculty=Faculty)

        student.set_password(rform.password.data)
        db.session.add(student)
        db.session.commit()

        login_user(student, remember=True)
        flash('Congratulations, you are now a registered user! Please check your email (and your spam folder) for a verification code.')
        return redirect(url_for('auth.verify'))
    return render_template('register.html', form=rform, Course=Course, Faculty=Faculty)


@auth.route('/auth/faculty/session', methods = ['GET', 'POST'])
def login_faculty():
    form = RegistrationFormFaculty()
    if form.validate_on_submit():
        fac_from_username = form.username.data
        fac_from_email = form.email.data         

        if fac_from_username is None or fac_from_email is None or fac_from_username.id != fac_from_email.id:
            flash('Selected username and email do not match.', 'error')
            return redirect(url_for('auth.faculty_session'))

        fac = fac_from_username  

        if not fac.check_password(form.password.data):
            flash('Invalid password.', 'error')
            return redirect(url_for('auth.faculty_session'))

        login_user(fac, remember=True)
        flash(f'The user {fac.username} has successfully logged in!')
        return redirect(url_for('faculty.faculty_index', faculty_id=fac.id))

    return render_template('login_faculty.html', form=form)

@auth.route('/auth/student/session', methods=['GET', 'POST'])
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
                if not user.verified:
                    return redirect(url_for('faculty.unverified'))
                flash('The user {} has successfully logged in!'.format(user.username))
                return redirect(url_for('faculty.faculty_index', faculty_id=user.id))

        flash('Invalid username, password or role selection.')
        return redirect(url_for('auth.login'))
    return render_template('login.html', form=lform)


@auth.route('/auth/new_verification', methods=['GET', 'POST'])
@login_required
def resend_verification():
    # Email the user their verification code
    vercode_unhashed = current_user.email + "SALT!!!"
    subject = "Your Verification Code For Research App"
    message = f"""
            Greetings, {current_user.username}!

            Please find your verification code below:

            **{hashlib.sha256(vercode_unhashed.encode('utf-8')).hexdigest()}**

            May your research be epic.

            Best wishes,
            Matvei "G-Chist" Shestopalov
            Head of Vibe Coding | Research App Development Team
            """

    send_email(current_user.email, subject, message)

    flash(
        'Please check your email (and your spam folder) for a verification code.')
    return redirect(url_for('auth.verify'))

@auth.route('/auth/email_verifications/', methods=['GET', 'POST'])
@login_required
def verify():
    form = VerificationForm()
    if form.validate_on_submit():
        vercode_unhashed = current_user.email + "SALT!!!"
        verification_code = hashlib.sha256(vercode_unhashed.encode('utf-8')).hexdigest()
        print(verification_code)
        if form.code.data == verification_code:
            current_user.verified = True
            db.session.commit()
            flash('Your account has been verified!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid verification code.')
    return render_template('verify.html', form=form)


@auth.route('/auth/session', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# @auth.route('/faculty/verify/<token>', methods = ['GET'])
# @auth.route('/faculty/login/sso', methods = ['GET'])
