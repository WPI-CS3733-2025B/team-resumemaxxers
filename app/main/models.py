from datetime import datetime, timezone
from typing import List, Optional

from app import db
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    user = db.session.get(Student, int(id))
    if user:
        return user
    return db.session.get(Faculty, int(id))

students_majors = sqla.Table(
    'students_majors',
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('major_id', sqla.Integer, sqla.ForeignKey('major.id'), primary_key=True)
)

students_research_topics = sqla.Table(
    'students_research_topics',
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('research_topic_name', sqla.String, sqla.ForeignKey('research_topic.name'), primary_key=True)
)

students_languages = sqla.Table(
    'students_languages',
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('language_name', sqla.String, sqla.ForeignKey('language.name'), primary_key=True)
)

positions_majors = sqla.Table(
    'positions_majors',
    db.metadata,
    sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('position.id'), primary_key=True),
    sqla.Column('major_id', sqla.Integer, sqla.ForeignKey('major.id'), primary_key=True)
)

positions_research_topics = sqla.Table(
    'positions_research_topics',
    db.metadata,
    sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('position.id'), primary_key=True),
    sqla.Column('research_topic_name', sqla.String, sqla.ForeignKey('research_topic.name'), primary_key=True)
)

positions_languages = sqla.Table(
    'positions_languages',
    db.metadata,
    sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('position.id'), primary_key=True),
    sqla.Column('language_name', sqla.String, sqla.ForeignKey('language.name'), primary_key=True)
)

positions_courses = sqla.Table(
    'positions_courses',
    db.metadata,
    sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('position.id'), primary_key=True),
    sqla.Column('course_id', sqla.Integer, sqla.ForeignKey('course.id'), primary_key=True)
)

course_majors = sqla.Table(
    'course_majors',
    db.metadata,
    sqla.Column('course_id', sqla.Integer, sqla.ForeignKey('course.id'), primary_key=True),
    sqla.Column('major_id', sqla.Integer, sqla.ForeignKey('major.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __abstract__ = True
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    username: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True, index=True)
    firstname: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64))
    lastname: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64))
    email: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120), unique=True, index=True)
    password_hash: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Student(User):
    __tablename__ = 'student'
    gpa: sqlo.Mapped[Optional[float]] = sqlo.mapped_column(sqla.Float)

    majors: sqlo.Mapped[List['Major']] = sqlo.relationship(secondary=students_majors, back_populates='students')
    research_topics: sqlo.Mapped[List['ResearchTopic']] = sqlo.relationship(secondary=students_research_topics, back_populates='students')
    languages: sqlo.Mapped[List['Language']] = sqlo.relationship(secondary=students_languages, back_populates='students')
    
    recommendations: sqlo.Mapped[List['Recommendation']] = sqlo.relationship(back_populates='student')
    applications: sqlo.Mapped[List['Application']] = sqlo.relationship(back_populates='student')
    courses: sqlo.Mapped[List['CourseEnrollment']] = sqlo.relationship(back_populates='student')

    def __repr__(self):
        return f'<Student {self.username}>'


class Faculty(User):
    __tablename__ = 'faculty'
    positions: sqlo.Mapped[List['Position']] = sqlo.relationship(back_populates='faculty')
    recommendations: sqlo.Mapped[List['Recommendation']] = sqlo.relationship(back_populates='faculty')

    def __repr__(self):
        return f'<Faculty {self.username}>'


class Application(db.Model):
    __tablename__ = 'application'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    student_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('student.id'))
    position_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('position.id'))
    statement: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(1500))
    status: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), default="pending")
    created_at: sqlo.Mapped[datetime] = sqlo.mapped_column(
        sqla.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    student: sqlo.Mapped['Student'] = sqlo.relationship(back_populates='applications')
    position: sqlo.Mapped['Position'] = sqlo.relationship(back_populates='applications')
    recommendations: sqlo.Mapped[list['Recommendation']] = sqlo.relationship(back_populates='application')

    def __repr__(self):
        return f'<Application {self.id}>'


class Position(db.Model):
    __tablename__ = 'position'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
    description: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(512))
    start_date: sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default=lambda: datetime.now(timezone.utc))
    end_date: sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default=lambda: datetime.now(timezone.utc))
    team_size: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer, default=1)
    min_gpa: sqlo.Mapped[Optional[float]] = sqlo.mapped_column(sqla.Float)
    faculty_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('faculty.id'))
    ref_required: sqlo.Mapped[bool] = sqlo.mapped_column(sqla.Boolean, default=False)

    faculty: sqlo.Mapped['Faculty'] = sqlo.relationship(back_populates='positions')
    applications: sqlo.Mapped[List['Application']] = sqlo.relationship(back_populates='position')
    
    majors: sqlo.Mapped[List['Major']] = sqlo.relationship(secondary=positions_majors, back_populates='positions')
    research_topics: sqlo.Mapped[List['ResearchTopic']] = sqlo.relationship(secondary=positions_research_topics, back_populates='positions')
    languages: sqlo.Mapped[List['Language']] = sqlo.relationship(secondary=positions_languages, back_populates='positions')
    courses: sqlo.Mapped[List['Course']] = sqlo.relationship(secondary=positions_courses, back_populates='positions')

    def __repr__(self):
        return f'<Position {self.name}>'


class Major(db.Model):
    __tablename__ = 'major'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100), unique=True)

    students: sqlo.Mapped[List['Student']] = sqlo.relationship(secondary=students_majors, back_populates='majors')
    positions: sqlo.Mapped[List['Position']] = sqlo.relationship(secondary=positions_majors, back_populates='majors')
    courses: sqlo.Mapped[List['Course']] = sqlo.relationship(secondary=course_majors, back_populates='majors')

    def __repr__(self):
        return f'<Major {self.name}>'


class Course(db.Model):
    __tablename__ = 'course'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
    coursenum: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10), index=True)

    majors: sqlo.Mapped[List['Major']] = sqlo.relationship(secondary = course_majors, back_populates='courses')
    students: sqlo.Mapped[List['CourseEnrollment']] = sqlo.relationship(back_populates='course')
    positions: sqlo.Mapped[List['Position']] = sqlo.relationship(secondary=positions_courses, back_populates='courses')

    def __repr__(self):
        return f'<Course {self.name}>'


class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    student_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('student.id'))
    faculty_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('faculty.id'))
    application_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('application.id'))
    status: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), default="pending")

    student: sqlo.Mapped['Student'] = sqlo.relationship(back_populates='recommendations')
    faculty: sqlo.Mapped['Faculty'] = sqlo.relationship(back_populates='recommendations')
    application: sqlo.Mapped['Application'] = sqlo.relationship(back_populates='recommendations')

    def __repr__(self):
        return f'<Recommendation {self.id}>'


class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollment'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    student_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('student.id'))
    course_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('course.id'))
    grade: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(2))
    instructor_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('faculty.id'))

    student: sqlo.Mapped['Student'] = sqlo.relationship(back_populates='courses')
    course: sqlo.Mapped['Course'] = sqlo.relationship(back_populates='students')
    instructor: sqlo.Mapped['Faculty'] = sqlo.relationship()


    def __repr__(self):
        return f'<CourseEnrollment {self.id}>'


class ResearchTopic(db.Model):
    __tablename__ = 'research_topic'
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100), primary_key=True)

    students: sqlo.Mapped[List['Student']] = sqlo.relationship(secondary=students_research_topics, back_populates='research_topics')
    positions: sqlo.Mapped[List['Position']] = sqlo.relationship(secondary=positions_research_topics, back_populates='research_topics')

    def __repr__(self):
        return f'<ResearchTopic {self.name}>'


class Language(db.Model):
    __tablename__ = 'language'
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100), primary_key=True)

    students: sqlo.Mapped[List['Student']] = sqlo.relationship(secondary=students_languages, back_populates='languages')
    positions: sqlo.Mapped[List['Position']] = sqlo.relationship(secondary=positions_languages, back_populates='languages')

    def __repr__(self):
        return f'<Language {self.name}>'

