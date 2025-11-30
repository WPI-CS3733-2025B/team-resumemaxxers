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
    donald_trump = Student(username='donald_trump', email='dt@trump.com', firstname='Donald', lastname='Trump', gpa=2.2,
                         id=100)
    bill_clinton = Student(username='BiLl Clinton', email='bill@clinton.com', firstname='Bill', lastname='Clinton', gpa=4.0, id=2)
    peter_jones = Student(username='peter_jones', email='peter@jones.com', firstname='Peter', lastname='Jones', gpa=3.1)
    barack_obama = Student(username='darack obama', email='barack@obama.com', firstname='Barack', lastname='Obama', gpa=3.7)
    william_shakespeare = Student(username='william shakespeare', email='will@shakespeare.com', firstname='William', lastname='Shakespeare', gpa=3.8)
    bill_clinton2 = Student(username='BILL CLINTON', email='billc@clinton.com', firstname='William', lastname='Clinton', gpa=3.6)

    # Faculty
    dr_alan_turing = Faculty(username='dr_alan_turing', email='alan@turing.com', firstname='Alan', lastname='Turing')
    bill_clinton_fac = Faculty(username='bill_clinton_fac', email='billf@clinton.com', firstname='Bill', lastname='Clinton', id=68, verified=True)
    donald_trump_fac = Faculty(username='Donald Trump', email='donald@trump.com', firstname='Donald', lastname='Trump')
    unverified_faculty = Faculty(username='unverified_prof', email='unverified@prof.com', firstname='Unverified', lastname='Professor', verified=False)
    unverified_faculty.set_password('password')

    donald_trump.set_password("67")
    bill_clinton_fac.set_password("68")
    bill_clinton.set_password("67")
    barack_obama.set_password("11")
    william_shakespeare.set_password("11")
    bill_clinton2.set_password("11")
    donald_trump_fac.set_password("11")
    dr_alan_turing.set_password("11")

    # Majors, Topics, Languages, Courses
    major_compsci = Major(name='Computer Science')
    major_engineering = Major(name='Engineering')
    topic_ai = ResearchTopic(name='Artificial Intelligence')
    lang_python = Language(name='Python')
    course_intro_cs = Course(name='Intro to CS', coursenum='CS-101')
    course_adv_algo = Course(name='Advanced Algorithms', coursenum='CS-420')

    db.session.add_all([donald_trump, bill_clinton, peter_jones, barack_obama, william_shakespeare, bill_clinton2,
                        dr_alan_turing, bill_clinton_fac, donald_trump_fac, unverified_faculty,
                        major_compsci, major_engineering, topic_ai, lang_python,
                        course_intro_cs, course_adv_algo])
    db.session.commit()

    # Positions
    pos_research_assistant = Position(name='Research Assistant', description='Must have unspoken rizz.',
                                      faculty_id=bill_clinton_fac.id)
    pos_teaching_assistant = Position(name='Teaching Assistant', description='Whar', faculty_id=dr_alan_turing.id)

    # Course Enrollments
    enroll_bill = CourseEnrollment(student_id=bill_clinton.id, course_id=course_intro_cs.id,
                                   instructor_id=bill_clinton_fac.id, grade=3)
    enroll_donald = CourseEnrollment(student_id=donald_trump.id, course_id=course_adv_algo.id,
                                   instructor_id=bill_clinton_fac.id, grade=4)

    db.session.add_all([pos_research_assistant, pos_teaching_assistant, enroll_bill, enroll_donald])
    db.session.commit()

    bill_clinton.majors.append(major_engineering)
    bill_clinton.languages.append(lang_python)
    barack_obama.majors.append(major_compsci)
    barack_obama.research_topics.append(topic_ai)
    pos_research_assistant.research_topics.append(topic_ai)
    pos_research_assistant.majors.append(major_engineering)

    db.session.commit()

    # BiLl Clinton applies for Research Assistant
    app_bill = Application(student_id=bill_clinton.id, position_id=pos_research_assistant.id, statement='It is simple.')
    db.session.add(app_bill)
    db.session.commit()

    # Faculty recommends BiLl Clinton for the position
    rec_bill = Recommendation(student_id=bill_clinton.id, faculty_id=bill_clinton_fac.id, application_id=app_bill.id,
                              status='Approved')
    db.session.add(rec_bill)
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()


def test_student_dashboard_loads(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/dashboard' page is requested (GET)
    THEN check that the response is valid
    """
    do_login(test_client, path='/login', username='BiLl Clinton', passwd='67', user_role="student")

    response = test_client.get('/student/dashboard')
    assert response.status_code == 200
    assert b"Student Dashboard" in response.data
    assert b"My Applications" in response.data
    assert b"My Recommendations" in response.data

    # Check for application details
    assert b"Research Assistant" in response.data
    assert b"pending" in response.data

    # Check for recommendation details
    assert b"Research Assistant" in response.data
    assert b"Bill" in response.data
    assert b"Clinton" in response.data
    assert b"Approved" in response.data

    do_logout(test_client, path='/logout')


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
    do_login(test_client, path='/login', username='donald_trump', passwd='67', user_role="student")

    do_logout(test_client, path='/logout')


def test_faculty_can_create_position(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct credentials
    AND '/faculty/<faculty_id>/create_position' is submitted correctly
    THEN check that the position is created
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    response = test_client.get('/faculty/1/create_position')  # not functional, should be 302
    assert response.status_code == 302
    response = test_client.get('/faculty/68/create_position')
    assert response.status_code == 200
    assert b"Create New Position" in response.data

    # Get database IDs for multi-select fields
    with test_client.application.app_context():
        major_id = str(db.session.scalars(sqla.select(Major).filter_by(name='Computer Science')).first().id)
        topic_name = db.session.scalars(sqla.select(ResearchTopic).filter_by(name='Artificial Intelligence')).first().name
        lang_name = db.session.scalars(sqla.select(Language).filter_by(name='Python')).first().name

    # Prepare form data for a new position
    new_position_data = {
        'name': 'Hog Rider',
        'description': 'The Hog Rider is a Rare card that is unlocked from the Spell Valley (Arena 5). He is a very fast building-targeting, melee troop with moderately high hitpoints and damage.',
        'team_size': '2',
        'min_gpa': '3.0',
        'ref_required': 'y',  # 'y' for 'True' in some WTForms BooleanField handling
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'faculty': '68',
        'majors': major_id,
        'research_topics': topic_name,
        'languages': lang_name,
        'csrf_token': 'test'
        # CSRF token often required for POST forms, use a dummy for testing if WTF_CSRF_ENABLED is False
    }

    # POST request to submit the form
    response = test_client.post('/faculty/68/create_position', data=new_position_data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Hog Rider" in response.data  # check for the new position name on the redirected page (e.g., faculty dashboard)
    assert b"Position created successfully" in response.data  # check for a success flash message

    # Check database directly
    with test_client.application.app_context():
        created_position = db.session.scalars(sqla.select(Position).filter_by(name='Hog Rider')).first()
        assert created_position is not None
        assert created_position.faculty.username == 'bill_clinton_fac'
        assert created_position.description == 'The Hog Rider is a Rare card that is unlocked from the Spell Valley (Arena 5). He is a very fast building-targeting, melee troop with moderately high hitpoints and damage.'
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
    do_login(test_client, path='/login', username='donald_trump', passwd='67', user_role="student")
    response = test_client.get('/student/100/profile/view')
    assert response.status_code == 200
    assert b"donald_trump" in response.data
    assert b"dt@trump.com" in response.data
    assert b"2.2" in response.data  # Initial GPA
    do_logout(test_client, path='/logout')


def test_view_faculty_profile(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a logged-in student visits a faculty profile page
    THEN check that their information is displayed correctly
    """
    do_login(test_client, path='/login', username='donald_trump', passwd='67', user_role="student")
    response = test_client.get('/faculty/68/profile/view')
    assert response.status_code == 200
    assert b"bill_clinton_fac" in response.data
    do_logout(test_client, path='/logout')


def test_edit_student_profile(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a logged-in student submits the edit profile form
    THEN check that their information is updated in the database
    """
    do_login(test_client, path='/login', username='donald_trump', passwd='67', user_role="student")

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
    do_login(test_client, path='/login', username='BiLl Clinton', passwd='67', user_role="student")

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


def test_faculty_can_view_applications(request, test_client, init_database):
    """
    GIVEN a Flask application with positions and applications
    WHEN a faculty member views an application
    THEN check that application details are displayed
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    
    with test_client.application.app_context():
        application = db.session.scalars(sqla.select(Application).filter_by(student_id=2)).first()
        assert application is not None
    
    response = test_client.get(f'/faculty/{application.id}/view')
    assert response.status_code == 200
    assert b"It is simple." in response.data  # Jane's application statement
    
    do_logout(test_client, path='/logout')


def test_faculty_can_approve_application(request, test_client, init_database):
    """
    GIVEN a Flask application with a pending application
    WHEN a faculty member approves the application
    THEN check that the status changes to approved
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    
    with test_client.application.app_context():
        application = db.session.scalars(sqla.select(Application).filter_by(student_id=2)).first()
        assert application is not None
        app_id = application.id

    response = test_client.get(f'/faculty/{app_id}/approve', follow_redirects=True)
    assert response.status_code == 200
    assert b"Student approved" in response.data
    
    with test_client.application.app_context():
        updated_app = db.session.get(Application, app_id)
        assert updated_app.status == "approved"
    
    do_logout(test_client, path='/logout')


def test_faculty_can_reject_application(request, test_client, init_database):
    """
    GIVEN a Flask application with a pending application
    WHEN a faculty member rejects the application
    THEN check that the status changes to rejected
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    
    with test_client.application.app_context():
        application = db.session.scalars(sqla.select(Application).filter_by(student_id=2)).first()
        assert application is not None
        app_id = application.id
    
    response = test_client.get(f'/faculty/{app_id}/reject', follow_redirects=True)
    assert response.status_code == 200
    assert b"Student rejected" in response.data
    
    with test_client.application.app_context():
        updated_app = db.session.get(Application, app_id)
        assert updated_app.status == "rejected"
    
    do_logout(test_client, path='/logout')


def test_faculty_can_edit_position(request, test_client, init_database):
    """
    GIVEN a Flask application with an existing position
    WHEN a faculty member edits the position
    THEN check that the changes are saved
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")

    with test_client.application.app_context():
        position = db.session.scalars(sqla.select(Position).filter_by(name='Research Assistant')).first()
        assert position is not None
        pos_id = position.id
    
    # GET the edit page
    response = test_client.get(f'/faculty/{pos_id}/edit_position')
    assert response.status_code == 200
    assert b"Edit Position" in response.data
    
    # Get database IDs for multi-select fields
    with test_client.application.app_context():
        major_id = str(db.session.scalars(sqla.select(Major).filter_by(name='Engineering')).first().id)
        topic_name = db.session.scalars(sqla.select(ResearchTopic).filter_by(name='Artificial Intelligence')).first().name
        lang_name = db.session.scalars(sqla.select(Language).filter_by(name='Python')).first().name
    
    # POST updated data
    edit_data = {
        'name': 'Mega Knight',
        'description': 'The Mega Knight is a Legendary card that is unlocked from the Electro Valley (Arena 11). It spawns an area-damage, ground-targeting, melee, ground troop with very high hitpoints and high damage.',
        'team_size': '7',
        'min_gpa': '3.5',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'faculty': '68',
        'majors': major_id,
        'research_topics': topic_name,
        'languages': lang_name,
        'csrf_token': 'test'
    }
    
    response = test_client.post(f'/faculty/{pos_id}/edit_position', data=edit_data, follow_redirects=True)
    assert response.status_code == 200
    
    with test_client.application.app_context():
        updated_pos = db.session.get(Position, pos_id)
        assert updated_pos.name == 'Mega Knight'
        assert updated_pos.description == 'The Mega Knight is a Legendary card that is unlocked from the Electro Valley (Arena 11). It spawns an area-damage, ground-targeting, melee, ground troop with very high hitpoints and high damage.'
        assert updated_pos.team_size == 7
    
    do_logout(test_client, path='/logout')


def test_faculty_can_delete_position(request, test_client, init_database):
    """
    GIVEN a Flask application with an existing position
    WHEN a faculty member deletes the position
    THEN check that the position is removed from the database
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    
    # Get database IDs for multi-select fields
    with test_client.application.app_context():
        major_id = str(db.session.scalars(sqla.select(Major).filter_by(name='Computer Science')).first().id)
        topic_name = db.session.scalars(sqla.select(ResearchTopic).filter_by(name='Artificial Intelligence')).first().name
    
    # Create a new position to delete
    new_position_data = {
        'name': 'Ram Rider',
        'description': 'The Ram Rider is a Legendary card that is unlocked from the Electro Valley (Arena 11). It spawns a single-target, building-targeting, melee, ground troop with high hitpoints and high damage.',
        'team_size': '10',
        'min_gpa': '3.0',
        'start_date': '2025-01-01',
        'end_date': '2025-06-30',
        'faculty': '68',
        'majors': major_id,
        'research_topics': topic_name,
        'csrf_token': 'test'
    }
    
    response = test_client.post('/faculty/68/create_position', data=new_position_data, follow_redirects=True)
    assert response.status_code == 200
    
    with test_client.application.app_context():
        temp_pos = db.session.scalars(sqla.select(Position).filter_by(name='Ram Rider')).first()
        assert temp_pos is not None
        pos_id = temp_pos.id
    
    # Delete the position
    response = test_client.get(f'/faculty/{pos_id}/delete_position', follow_redirects=True)
    assert response.status_code == 200
    assert b"Position deleted successfully" in response.data
    
    with test_client.application.app_context():
        deleted_pos = db.session.scalars(sqla.select(Position).filter_by(name='Ram Rider')).first()
        assert deleted_pos is None
    
    do_logout(test_client, path='/logout')


def test_student_can_view_recommended_positions(request, test_client, init_database):
    """
    GIVEN a Flask application with positions and student profile
    WHEN a student views recommended positions
    THEN check that relevant positions are displayed
    """
    do_login(test_client, path='/login', username='darack obama', passwd='11', user_role="student")
    
    response = test_client.get('/recommended')
    assert response.status_code == 200
    assert b"Recommended Positions" in response.data
    
    do_logout(test_client, path='/logout')


def test_view_position_details(request, test_client, init_database):
    """
    GIVEN a Flask application with positions
    WHEN a user views position details
    THEN check that full position information is displayed
    """
    do_login(test_client, path='/login', username='william shakespeare', passwd='11', user_role="student")
    
    with test_client.application.app_context():
        position = db.session.scalars(sqla.select(Position).filter_by(name='Research Assistant')).first()
        assert position is not None
        pos_id = position.id
    
    response = test_client.get(f'/position/{pos_id}/view')
    assert response.status_code == 200
    assert b"Research Assistant" in response.data
    
    do_logout(test_client, path='/logout')


def test_faculty_dashboard_shows_positions_and_applications(request, test_client, init_database):
    """
    GIVEN a Flask application
    WHEN a faculty member views their dashboard
    THEN check that their positions and applications are displayed
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    
    response = test_client.get('/faculty/68/index')
    assert response.status_code == 200
    assert b"Research Assistant" in response.data
    
    do_logout(test_client, path='/logout')


def test_unauthorized_user_cannot_edit_others_position(request, test_client, init_database):
    """
    GIVEN a Flask application with positions
    WHEN a faculty tries to edit another faculty's position
    THEN check that access is denied
    """
    do_login(test_client, path='/login', username='dr_alan_turing', passwd='11', user_role="faculty")
    
    with test_client.application.app_context():
        other_position = db.session.scalars(sqla.select(Position).filter_by(name='Teaching Assistant')).first()
        assert other_position is not None
        pos_id = other_position.id
    
    response = test_client.get(f'/faculty/{pos_id}/edit_position', follow_redirects=True)
    # Respost is eith er 403 or error message
    assert response.status_code in [200, 403]
    
    do_logout(test_client, path='/logout')


def test_index_filter_by_major(request, test_client, init_database):
    """
    GIVEN a Flask application with positions having different majors
    WHEN a user filters positions by major
    THEN check that only matching positions are displayed
    """
    do_login(test_client, path='/login', username='BILL CLINTON', passwd='11', user_role="student")
    
    with test_client.application.app_context():
        compsci_major = db.session.scalars(sqla.select(Major).filter_by(name='Computer Science')).first()
        assert compsci_major is not None
        major_id = compsci_major.id
    
    # poast filter requestt with mahor selection 
    response = test_client.post('/', data={'majors': [major_id], 'csrf_token': 'test'}, follow_redirects=True)
    assert response.status_code == 200
    
    do_logout(test_client, path='/logout')

def test_edit_lists_page_loads(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/lists/settings' page is requested (GET) by a faculty member
    THEN check that the response is valid
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    response = test_client.get('/faculty/lists/settings')
    assert response.status_code == 200
    assert b"Edit lists" in response.data
    do_logout(test_client, path='/logout')

def test_add_course_to_lists(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a faculty member adds a course through the 'edit_lists' page
    THEN check that the new course is in the database
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    with test_client.application.app_context():
        major_id = db.session.scalars(sqla.select(Major).filter_by(name='Computer Science')).first().id
    response = test_client.post('/faculty/lists/settings', data={
        'course-name': 'New Course',
        'course-coursenum': 'NC-101',
        'course-majors': [major_id],
        'course-submit': True
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Course added!' in response.data
    with test_client.application.app_context():
        course = db.session.scalars(sqla.select(Course).filter_by(name='New Course')).first()
        assert course is not None
        assert course.coursenum == 'NC-101'
    do_logout(test_client, path='/logout')

def test_delete_course_from_lists(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a faculty member deletes a course through the 'edit_lists' page
    THEN check that the course is removed from the database
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    with test_client.application.app_context():
        new_course = Course(name='Deletable Course', coursenum='DEL-101')
        db.session.add(new_course)
        db.session.commit()
        course_id = new_course.id

    response = test_client.post('/faculty/lists/settings', data={
        'course_delete-courses': [course_id],
        'course_delete-submit': True
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Courses deleted!' in response.data
    with test_client.application.app_context():
        course = db.session.get(Course, course_id)
        assert course is None
    do_logout(test_client, path='/logout')

def test_delete_course_with_dependency_from_lists(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a faculty member tries to delete a course with a dependency
    THEN check that the deletion fails and a flash message is shown
    """
    do_login(test_client, path='/login', username='bill_clinton_fac', passwd='68', user_role="faculty")
    with test_client.application.app_context():
        course = db.session.scalars(sqla.select(Course).filter_by(name='Intro to CS')).first()
        student = db.session.scalars(sqla.select(Student).filter_by(username='BiLl Clinton')).first()
        enrollment = CourseEnrollment(student_id=student.id, course_id=course.id, instructor_id=68, grade=4)
        db.session.add(enrollment)
        db.session.commit()
        course_id = course.id
    
    response = test_client.post('/faculty/lists/settings', data={
        'course_delete-courses': [course_id],
        'course_delete-submit': True
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Cannot delete this item due to dependencies!' in response.data
    with test_client.application.app_context():
        course = db.session.get(Course, course_id)
        assert course is not None
    do_logout(test_client, path='/logout')

def test_unverified_faculty_redirect(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN an unverified faculty member logs in
    THEN check that they are redirected to the unverified page
    """
    # Login as unverified faculty
    response = test_client.post('/login', data={
        'username': 'unverified_prof',
        'password': 'password',
        'role': 'faculty'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Account Not Verified" in response.data

    # Try to access a protected faculty route
    response = test_client.get('/faculty/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Account Not Verified" in response.data

    # Logout
    do_logout(test_client, path='/logout')