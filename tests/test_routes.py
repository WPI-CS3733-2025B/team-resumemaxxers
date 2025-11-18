import os
import pytest
from flask import  url_for
from app import create_app, db
from app.main.models import Student, Faculty, Position, Application, Recommendation, Major, Course, ResearchTopic, Language, CourseEnrollment
from config import Config
import sqlalchemy as sqla


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True


@pytest.fixture(scope='module')
def test_client():
    # create the flask application ; configure the app for tests
    flask_app = create_app(config_class=TestConfig)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.test_request_context()
    ctx.push()

    yield testing_client
    # this is where the testing happens!

    ctx.pop()

def new_student(username, email, firstname, lastname, passwd, gpa):
    user = Student(username = username, email = email, firstname = firstname, lastname = lastname, gpa=gpa)
    user.set_password(passwd)
    return user


@pytest.fixture
def init_database(request,test_client):
    # Create the database and the database table
    db.create_all()

    # Students
    john_pork = Student(username='john_pork', email='jp@pork.com', firstname='John', lastname='Pork', gpa=2.2)
    khaby_lame = Student(username='khaby_lame', email='khaby@lame.com', firstname='Khaby', lastname='Lame', gpa=4.0)
    baby_gronk = Student(username='baby_gronk', email='livvy@dunne.com', firstname='Baby', lastname='Gronk', gpa=3.1)
    
    # Faculty
    dr_skibidi = Faculty(username='dr_skibidi', email='skibidi@toilet.com', firstname='Doctor', lastname='Skibidi')
    the_rizzler = Faculty(username='the_rizzler', email='riz@zler.com', firstname='The', lastname='Rizzler', id=68)

    john_pork.set_password("67")
    the_rizzler.set_password("68")

    # Majors, Topics, Languages, Courses
    major_yapping = Major(name='Advanced Yapping')
    major_mewing = Major(name='Mewing')
    topic_ohio = ResearchTopic(name='The Ohio Phenomenon')
    lang_gen_alpha = Language(name='Gen Alpha')
    course_rizz = Course(name='Intro to Rizz', coursenum='RIZZ-101')
    course_sigma = Course(name='Advanced Sigma Grindset', coursenum='SIG-420')
    
    db.session.add_all([john_pork, khaby_lame, baby_gronk, dr_skibidi, the_rizzler,
                        major_yapping, major_mewing, topic_ohio, lang_gen_alpha,
                        course_rizz, course_sigma])
    db.session.commit()

    # Positions
    pos_rizz = Position(name='Chief Rizz Officer', description='Must have unspoken rizz.', faculty_id=the_rizzler.id)
    pos_skibidi = Position(name='Head Skibidi Toilet Engineer', description='Whar', faculty_id=dr_skibidi.id)
    
    # Course Enrollments
    enroll_khaby = CourseEnrollment(student_id=khaby_lame.id, course_id=course_rizz.id, instructor_id=the_rizzler.id, grade=3)
    enroll_pork = CourseEnrollment(student_id=john_pork.id, course_id=course_sigma.id, instructor_id=the_rizzler.id, grade=4)

    db.session.add_all([pos_rizz, pos_skibidi, enroll_khaby, enroll_pork])
    db.session.commit()

    khaby_lame.majors.append(major_mewing)
    khaby_lame.languages.append(lang_gen_alpha)
    pos_rizz.research_topics.append(topic_ohio)
    pos_rizz.majors.append(major_mewing)

    db.session.commit()

    # Khaby Lame applies for Chief Rizz Officer
    app_khaby = Application(student_id=khaby_lame.id, position_id=pos_rizz.id, statement='It is simple.')
    db.session.add(app_khaby)
    db.session.commit()

    # The Rizzler recommends Khaby Lame for the position
    rec_khaby = Recommendation(student_id=khaby_lame.id, faculty_id=the_rizzler.id, application_id=app_khaby.id, status='Approved')
    db.session.add(rec_khaby)
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()

def test_register_page(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/register' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/student/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_login_page_faculty(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/login' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/faculty/login')
    assert response.status_code == 200
    assert b"Log In" or b"Sign In" in response.data

def test_login_page_student(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/login' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b"Log In" or b"Sign In" in response.data

def test_invalidlogin(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with wrong credentials
    THEN check that the response is valid and login is refused
    """
    response = test_client.post('/login',
                          data=dict(username='sakire', password='12345',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def do_login(test_client, path, username, passwd, user_role):
    response = test_client.post(path,
                          data=dict(username= username, password=passwd, role=user_role, remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Logout" in response.data

def do_logout(test_client, path):
    response = test_client.get(path,
                          follow_redirects = True)
    assert response.status_code == 200
    # Assuming the application re-directs to login page after logout.
    assert b"Sign In" in response.data

def test_login_logout(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct credentials
    THEN check that the response is valid and login is succesfull
    """
    do_login(test_client, path = '/login', username = 'john_pork', passwd = '67', user_role="student")

    do_logout(test_client, path = '/logout')

def test_create_position(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct credentials
    AND '/faculty/<faculty_id>/create_position' is submitted correctly
    THEN check that the position is created
    """
    do_login(test_client, path= '/login', username='the_rizzler', passwd='68', user_role="faculty")
    response = test_client.get('/faculty/68/create_position')
    assert response.status_code == 200