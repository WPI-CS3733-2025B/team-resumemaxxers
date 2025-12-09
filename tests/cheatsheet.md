## CS3733 CHEAT SHEET (QUIZ 4: TESTS)
APP SETUP
```python
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
```
OR
```python
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
```
EXAMPLE TESTS:
```python
def test_login_with_invalid_credentials_fails_2(request, test_client, init_database):
	response = test_client.post('/auth/student/session',
			data=dict(username='sakire', password='12345', remember_me=False),
		follow_redirects=True)
	assert b"Sign In" in response.data
```
