import pytest
from appinit import make_shell_context, add_majors, add_interests, add_languages, add_courses, add_faculty, init_db
from app import create_app, db
from config import Config
from app.main.models import Major, ResearchTopic, Language, Course, Faculty

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_make_shell_context(app):
    with app.app_context():
        context = make_shell_context()
        assert 'sqla' in context
        assert 'sqlo' in context
        assert 'db' in context
        assert 'Major' in context
        assert 'Interest' in context
        assert 'Language' in context
        assert 'Course' in context
        assert 'Faculty' in context

def test_add_majors(app):
    with app.app_context():
        # Ensure no majors initially
        assert db.session.query(Major).count() == 0
        add_majors()
        assert db.session.query(Major).count() > 0
        # Ensure no duplicates on second call
        add_majors()
        count_after_second_call = db.session.query(Major).count()
        assert count_after_second_call == 17

def test_add_interests(app):
    with app.app_context():
        assert db.session.query(ResearchTopic).count() == 0
        add_interests()
        assert db.session.query(ResearchTopic).count() > 0
        add_interests()
        count_after_second_call = db.session.query(ResearchTopic).count()
        assert count_after_second_call == 14

def test_add_languages(app):
    with app.app_context():
        assert db.session.query(Language).count() == 0
        add_languages()
        assert db.session.query(Language).count() > 0
        add_languages()
        count_after_second_call = db.session.query(Language).count()
        assert count_after_second_call == 8

def test_add_courses(app):
    with app.app_context():
        assert db.session.query(Course).count() == 0
        add_courses()
        assert db.session.query(Course).count() > 0
        add_courses()
        count_after_second_call = db.session.query(Course).count()
        assert count_after_second_call == 17

def test_add_faculty(app):
    with app.app_context():
        assert db.session.query(Faculty).count() == 0
        add_faculty()
        assert db.session.query(Faculty).count() > 0
        add_faculty()
        count_after_second_call = db.session.query(Faculty).count()
        assert count_after_second_call == 3

def test_init_db_command(runner, app):
    with app.app_context():
        # Ensure db is empty before command
        db.drop_all()
        db.create_all()

        result = runner.invoke(init_db)
        assert 'Initialized the database.' in result.output
        assert Major.query.count() > 0
        assert ResearchTopic.query.count() > 0
        assert Language.query.count() > 0
        assert Course.query.count() > 0
        assert Faculty.query.count() > 0

