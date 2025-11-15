from app import db
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla

from app.main.models import Student
from app.auth.auth_forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth

@auth.route('/student/register', methods = ['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        student = Student( username = rform.username.data,
                           firstname = rform.firstname.data,
                           lastname = rform.lastname.data,
                           email = rform.email.data,
                           id = rform.id.data,
                           #major = ,
                           gpa = rform.gpa.data,
                           #research_topics = ,
                           #languages = ,
                           #courses = 
                           )
        student.set_password(rform.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    return render_template('register.html', form = rform)

'''
@auth.route('/faculty/register', methods = ['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        student = Student( username = rform.username.data,
                           firstname = rform.firstname.data,
                           lastname = rform.lastname.data,
                           email = rform.email.data,
                           address = rform.address.data)
        student.set_password(rform.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    return render_template('register.html', form = rform)
'''

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    lform = LoginForm()

    if lform.validate_on_submit():

        query = sqla.select(Student).where(Student.username == lform.username.data)
        student = db.session.scalars(query).first()

        if (student is None) or (student.check_password(lform.password.data) == False):
            return redirect(url_for('auth.login'))
        
        login_user(student, remember = lform.remember_me.data)
        flash('The user {} has successfully logged in!'.format(current_user.username))
        return redirect(url_for('main.index'))
    return render_template('login.html', form = lform)

@auth.route('/logout', methods = ['GET'])
@login_required 
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#@auth.route('/faculty/verify/<token>', methods = ['GET'])
#@auth.route('/faculty/login/sso', methods = ['GET'])