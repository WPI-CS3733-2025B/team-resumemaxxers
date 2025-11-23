import os
import pytest
from flask import url_for
from app import create_app, db
from app.main.models import Student, Faculty, Position, Application, Recommendation, Major, Course, ResearchTopic,     Language, CourseEnrollment
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
    user = Student(username=username, email=email, firstname=firstname, lastname=lastname, gpa=gpa)
    user.set_password(passwd)
    return user


@pytest.fixture
def init_database(request, test_client):
    # Create the database and the database table
    db.create_all()

    # Students
    john_smith = Student(username='john_smith', email='js@smith.com', firstname='John', lastname='Smith', gpa=2.2,
                         id=100)
    jane_doe = Student(username='jane_doe', email='jane@doe.com', firstname='Jane', lastname='Doe', gpa=4.0)
    peter_jones = Student(username='peter_jones', email='peter@jones.com', firstname='Peter', lastname='Jones', gpa=3.1)

    # Faculty
    dr_alan_turing = Faculty(username='dr_alan_turing', email='alan@turing.com', firstname='Alan', lastname='Turing')
    dr_grace_hopper = Faculty(username='dr_grace_hopper', email='grace@hopper.com', firstname='Grace',
                              lastname='Hopper', id=68)

    john_smith.set_password("67")
    dr_grace_hopper.set_password("68")

    # Majors, Topics, Languages, Courses
    major_compsci = Major(name='Computer Science')
    major_engineering = Major(name='Engineering')
    topic_ai = ResearchTopic(name='Artificial Intelligence')
    lang_python = Language(name='Python')
    course_intro_cs = Course(name='Intro to CS', coursenum='CS-101')
    course_adv_algo = Course(name='Advanced Algorithms', coursenum='CS-420')

    db.session.add_all([john_smith, jane_doe, peter_jones, dr_alan_turing, dr_grace_hopper,
                        major_compsci, major_engineering, topic_ai, lang_python,
                        course_intro_cs, course_adv_algo])
    db.session.commit()

    # Positions
    pos_research_assistant = Position(name='Research Assistant', description='Must have unspoken rizz.',
                                      faculty_id=dr_grace_hopper.id)
    pos_teaching_assistant = Position(name='Teaching Assistant', description='Whar', faculty_id=dr_alan_turing.id)

    # Course Enrollments
    enroll_jane = CourseEnrollment(student_id=jane_doe.id, course_id=course_intro_cs.id,
                                   instructor_id=dr_grace_hopper.id, grade=3)
    enroll_john = CourseEnrollment(student_id=john_smith.id, course_id=course_adv_algo.id,
                                   instructor_id=dr_grace_hopper.id, grade=4)

    db.session.add_all([pos_research_assistant, pos_teaching_assistant, enroll_jane, enroll_john])
    db.session.commit()

    jane_doe.majors.append(major_engineering)
    jane_doe.languages.append(lang_python)
    pos_research_assistant.research_topics.append(topic_ai)
    pos_research_assistant.majors.append(major_engineering)

    db.session.commit()

    # Jane Doe applies for Research Assistant
    app_jane = Application(student_id=jane_doe.id, position_id=pos_research_assistant.id, statement='It is simple.')
    db.session.add(app_jane)
    db.session.commit()

    # Dr. Grace Hopper recommends Jane Doe for the position
    rec_jane = Recommendation(student_id=jane_doe.id, faculty_id=dr_grace_hopper.id, application_id=app_jane.id,
                              status='Approved')
    db.session.add(rec_jane)
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()


def test_student_registration_page_loads(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/register' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/student/register')
    assert response.status_code == 200
    assert b"Register" in response.data


def test_faculty_login_page_loads(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/login' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/faculty/login')
    assert response.status_code == 200
    assert b"Log In" or b"Sign In" in response.data


def test_student_login_page_loads(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/login' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b"Log In" or b"Sign In" in response.data


def test_login_with_invalid_credentials_fails(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with wrong credentials
    THEN check that the response is valid and login is refused
    """
    response = test_client.post('/login',
                                data=dict(username='sakire', password='12345', remember_me=False),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def do_login(test_client, path, username, passwd, user_role):
    response = test_client.post(path,
                                data=dict(username=username, password=passwd, role=user_role, remember_me=False),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b"Logout" in response.data

def do_logout(test_client, path):
    response = test_client.get(path,
                               follow_redirects=True)
    assert response.status_code == 200
    # Assuming the application re-directs to login page after logout.
    assert b"Sign In" in response.data

def test_student_login_and_logout_succeeds(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct credentials
    THEN check that the response is valid and login is succesfull
    """
    do_login(test_client, path='/login', username='john_smith', passwd='67', user_role="student")

    do_logout(test_client, path='/logout')


def test_faculty_can_create_position(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct credentials
    AND '/faculty/<faculty_id>/create_position' is submitted correctly
    THEN check that the position is created
    """
    do_login(test_client, path='/login', username='dr_grace_hopper', passwd='68', user_role="faculty")
    response = test_client.get('/faculty/1/create_position')  # not functional, should be 302
    assert response.status_code == 302
    response = test_client.get('/faculty/68/create_position')
    assert response.status_code == 200
    assert b"Create New Position" in response.data

    # Prepare form data for a new position
    new_position_data = {
        'name': 'Meme Historian',
        'description': 'Research, catalog, and analyze',
        'team_size': '2',
        'min_gpa': '3.0',
        'ref_required': 'y',  # 'y' for 'True' in some WTForms BooleanField handling
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'csrf_token': 'test'
        # CSRF token often required for POST forms, use a dummy for testing if WTF_CSRF_ENABLED is False
    }

    # POST request to submit the form
    response = test_client.post('/faculty/68/create_position', data=new_position_data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Meme Historian" in response.data  # check for the new position name on the redirected page (e.g., faculty dashboard)
    assert b"Position created successfully" in response.data  # check for a success flash message

    # Check database directly
    with test_client.application.app_context():
        created_position = db.session.scalars(sqla.select(Position).filter_by(name='Meme Historian')).first()
        assert created_position is not None
        assert created_position.faculty.username == 'dr_grace_hopper'
        assert created_position.description == 'Research, catalog, and analyze'
        assert created_position.team_size == 2
        assert created_position.min_gpa == 3.0
        assert created_position.ref_required == True
        assert created_position.start_date is not None
        assert created_position.end_date is not None

    do_logout(test_client, path='/logout')


def test_student_can_view_own_profile(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a logged-in student visits their profile page
    THEN check that their information is displayed correctly
    """
    do_login(test_client, path='/login', username='john_smith', passwd='67', user_role="student")
    response = test_client.get('/student/100/profile/view')
    assert response.status_code == 200
    assert b"john_smith" in response.data
    assert b"js@smith.com" in response.data
    assert b"2.2" in response.data  # Initial GPA
    do_logout(test_client, path='/logout')


def test_view_faculty_profile(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a logged-in student visits a faculty profile page
    THEN check that their information is displayed correctly
    """
    do_login(test_client, path='/login', username='john_smith', passwd='67', user_role="student")
    response = test_client.get('/faculty/68/profile/view')
    assert response.status_code == 200
    assert b"dr_grace_hopper" in response.data
    do_logout(test_client, path='/logout')


def test_edit_student_profile(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a logged-in student submits the edit profile form
    THEN check that their information is updated in the database
    """
    do_login(test_client, path='/login', username='john_smith', passwd='67', user_role="student")

    # GET the edit page first
    response = test_client.get('/student/edit_profile')
    assert response.status_code == 200
    assert b"Edit Profile" in response.data

    # Get the ID of the major 'Computer Science' to add it to the student
    with test_client.application.app_context():
        compsci_major = db.session.scalars(sqla.select(Major).filter_by(name='Computer Science')).first()
        assert compsci_major is not None
        compsci_major_id = compsci_major.id

    # Prepare form data for editing the profile
    edit_profile_data = {
        'gpa': 3.4,
        'majors': compsci_major_id,
        'csrf_token': 'test'
    }

    # POST the new data
    response = test_client.post('/student/edit_profile', data=edit_profile_data, follow_redirects=True)

    response = test_client.get('/student/100/profile/view')

    # Assert the response after redirect
    assert response.status_code == 200
    assert b"3.4" in response.data

def test_student_cannot_apply_twice(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a student tries to apply for the same position twice
    THEN the second application should be rejected
    """
    do_login(test_client, path='/login', username='john_smith', passwd='67', user_role="student")

    with test_client.application.app_context():
        position = db.session.scalars(sqla.select(Position).filter_by(name='Research Assistant')).first()
        assert position is not None

    # First application
    response = test_client.post(f'/position/{position.id}/apply', data={'statement': 'Test application'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Application submitted successfully!" in response.data

    # Second application
    response = test_client.post(f'/position/{position.id}/apply', data={'statement': 'Another test application'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"You have already applied for this position." in response.data

    do_logout(test_client, path='/logout')
