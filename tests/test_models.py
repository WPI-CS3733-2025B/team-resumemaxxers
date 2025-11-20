import warnings
warnings.filterwarnings("ignore")

import unittest
from app import create_app, db
from app.main.models import Student, Faculty, Position, Application, Recommendation, Major, ResearchTopic, Language, Course, CourseEnrollment
from config import Config


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

    def test_password_hashing(self):
        u = Student(username='susan', email='susan@example.com', firstname='Susan', lastname='Smith')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_apply_and_withdraw(self):
        # Create and commit initial users and position
        s1 = Student(username='john', email='john@example.com', gpa=3.5, firstname='John', lastname='Pork')
        f1 = Faculty(username='prof', email='prof@example.com', firstname='Professor', lastname='Pork')
        db.session.add_all([s1, f1])
        db.session.commit()
        
        p1 = Position(name='Test Position', faculty_id=f1.id)
        db.session.add(p1)
        db.session.commit()
        
        # Test initial state
        self.assertEqual(len(s1.applications), 0)

        # Test applying to a position
        s1.apply(p1)
        self.assertEqual(len(s1.applications), 1)
        self.assertEqual(s1.applications[0].position_id, p1.id)

        # Test applying to the same position again (should do nothing)
        s1.apply(p1)
        self.assertEqual(len(s1.applications), 1)

        # Test withdrawing from the position
        s1.withdraw(p1)
        self.assertEqual(len(s1.applications), 0)

        # Test withdrawing again (should do nothing)
        s1.withdraw(p1)
        self.assertEqual(len(s1.applications), 0)

    def test_user_roles_and_get_id(self):
        s = Student(username='student1', email='s1@example.com', firstname='First', lastname='Student')
        f = Faculty(username='faculty1', email='f1@example.com', firstname='First', lastname='Faculty')
        db.session.add_all([s, f])
        db.session.commit()
        
        self.assertEqual(s.role, 'student')
        self.assertEqual(f.role, 'faculty')
        self.assertEqual(s.get_id(), f'student-{s.id}')
        self.assertEqual(f.get_id(), f'faculty-{f.id}')
        
    def test_relationships(self):
        # Create entities
        s = Student(username='rel_student', email='rel@s.com', gpa=4.0, firstname='Rel', lastname='Student')
        f = Faculty(username='rel_faculty', email='rel@f.com', firstname='Rel', lastname='Faculty')
        c = Course(name='SWE', coursenum='CS3733')
        m = Major(name='Computer Science')
        l = Language(name='Rust')
        rt = ResearchTopic(name='Artificial Intelligence')
        
        db.session.add_all([s, f, m, rt])
        db.session.commit()

        p = Position(name='AI Researcher', faculty_id=f.id, min_gpa=3.8)
        db.session.add(p)
        db.session.commit()
        
        # Associate relationships
        s.majors.append(m)
        s.research_topics.append(rt)
        p.majors.append(m)

        s.add_course(c, instructor=f)
        s.languages.append(l)
        s.add_research_topic(rt)
        
        db.session.commit()
        
        # Test relationships from Student side
        self.assertEqual(len(s.majors), 1)
        self.assertEqual(s.majors[0].name, 'Computer Science')
        self.assertIn(l, s.languages)
        self.assertIn(m, s.majors)
        
        # Test relationships from Position side
        self.assertEqual(len(p.majors), 1)
        self.assertEqual(p.majors[0].name, 'Computer Science')
        
        # Test back-population
        self.assertIn(s, m.students)
        self.assertIn(p, m.positions)

    def test_recommendation_flow(self):
        # Create entities
        s = Student(username='rec_student', email='rec@s.com', firstname='Rec', lastname='Student')
        f_poser = Faculty(username='rec_faculty_poser', email='rec_poser@f.com', firstname='Poser', lastname='Faculty')
        f_recommender = Faculty(username='rec_faculty_rec', email='rec_rec@f.com', firstname='Recommender', lastname='Faculty')
        db.session.add_all([s, f_poser, f_recommender])
        db.session.commit()

        p = Position(name='Position Requiring Refs', faculty_id=f_poser.id, ref_required=True)
        db.session.add(p)
        db.session.commit()
        
        # Student applies
        s.apply(p)
        self.assertEqual(len(s.applications), 1)
        application = s.applications[0]
        
        # Create and link a recommendation
        rec = Recommendation(
            student_id=s.id,
            faculty_id=f_recommender.id,
            application_id=application.id,
            status='Submitted'
        )
        db.session.add(rec)
        db.session.commit()
        
        # Check relationships
        self.assertEqual(len(application.recommendations), 1)
        self.assertEqual(application.recommendations[0].status, 'Submitted')
        self.assertIn(rec, s.recommendations)
        self.assertIn(rec, f_recommender.recommendations)

if __name__ == '__main__':
    unittest.main(verbosity=2)
