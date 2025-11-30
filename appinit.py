from config import Config

from app import create_app, db
from app.main.models import Major, ResearchTopic, Language, Course, Faculty, User
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

app = create_app(Config)
app.config['SECRET_KEY'] = 'REPLACE_LATER'

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'Major': Major, 'Interest': ResearchTopic, 'Language': Language, 'Course': Course, 'Faculty': Faculty, 'User': User}

majors = ["Aerospace Engineering", "Biomedical Engineering", "Chemical Engineering", "Civil Engineering", "Computer Science", "Electrical & Computer Engineering", "Environmental Engineering", "Industrial Engineering", "Data Science", "Robotics Engineering", "Mechanical Engineering", "Mathematical Sciences", "Physics", "Actuarial Mathematics", "Biology & Biotechnology", "Chemistry", "Management Information Systems"]
interests = ["Machine Learning", "High Performance Computing", "Artificial Intelligence", "Cybersecurity", "Knowledge Discovery & Data Mining", "Computer Graphics", "Human-Robot Interaction", "Biomechanics", "Sustainable Energy Systems", "Materials Science", "Bioinformatics", "Environmental Modeling", "Quantum Computing", "Game Development"]
languages = ["C", "C++", "Python", "Haskell", "Java", "JavaScript", "Lisp", "Rust"]
courses = ["CS1101", "CS1102", "CS2011", "CS220X", "CS2301", "CS3013", "CS3041", "CS3431", "CS3516", "CS3733", "CS4233", "CS4341", "CS4401", "CS4514", "CS4518", "CS4731", "CS4732"]

# Default faculty info table
fac_ids = [1, 2, 3]
fac_names = ["ab", "ac", "ad"]
fac_lastnames = ["bb", "bc", "bd"]
fac_passwords = ["11", "12", "13"]
#enter last name + name as username (no space)

# fill in db with some things

def add_majors():
    query = sqla.select(Major)
    if db.session.scalars(query).first() is None:
        majorsDict = [{"name":majors[i]} for i in range(len(majors))]
        # print(majorsDict)  # debugging
        for t in majorsDict:
            db.session.add(Major(name=t["name"]))
        db.session.commit()

def add_interests():
    query = sqla.select(ResearchTopic)
    if db.session.scalars(query).first() is None:
        interestsDict = [{"name":interests[i]} for i in range(len(interests))]
        for t in interestsDict:
            db.session.add(ResearchTopic(name=t["name"]))
        db.session.commit()

def add_languages():
    query = sqla.select(Language)
    if db.session.scalars(query).first() is None:
        languagesDict = [{"name":languages[i]} for i in range(len(languages))]
        for t in languagesDict:
            db.session.add(Language(name=t["name"]))
        db.session.commit()

def add_courses():
    query = sqla.select(Course)
    if db.session.scalars(query).first() is None:
        coursesDict = [{"name":courses[i], "coursenum": courses[i]} for i in range(len(courses))]
        for t in coursesDict:
            db.session.add(Course(name=t["name"], coursenum=t["coursenum"]))
        db.session.commit()

def add_faculty():
    query = sqla.select(Faculty)
    if db.session.scalars(query).first() is None:
        for i in range(len(fac_ids)):
            faculty = Faculty(
                username=fac_lastnames[i] + fac_names[i],
                email=fac_lastnames[i] + fac_names[i] + "@wpi.edu",
                firstname=fac_names[i],
                lastname=fac_lastnames[i]
            )
            faculty.set_password(fac_passwords[i])
            db.session.add(faculty)
        db.session.commit()

@app.cli.command("init-db")
def init_db():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    add_majors()
    add_interests()
    add_languages()
    add_courses()
    add_faculty()
    print("Initialized the database.")

if __name__ == "__main__":
    app.run(debug=True)