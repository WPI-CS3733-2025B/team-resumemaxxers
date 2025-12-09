from config import Config

from app import create_app, db
from app.main.models import Major, ResearchTopic, Language, Course, Faculty, User
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

app = create_app(Config)
app.config['SECRET_KEY'] = 'REPLACE_LATER'

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'Major': Major, 'Interest': ResearchTopic, 'Language': Language, 'Course': Course}

# WPI undergraduate majors
majors = [
    "Actuarial Mathematics",
    "Aerospace Engineering",
    "Architectural Engineering",
    "Biochemistry",
    "Biology and Biotechnology",
    "Biomedical Engineering",
    "Chemical Engineering",
    "Chemistry",
    "Civil Engineering",
    "Computer Science",
    "Data Science",
    "Electrical and Computer Engineering",
    "Environmental Engineering",
    "Industrial Engineering",
    "Interactive Media and Game Development",
    "Management Engineering",
    "Manufacturing Engineering",
    "Materials Science and Engineering",
    "Mathematical Sciences",
    "Mechanical Engineering",
    "Physics",
    "Professional Writing",
    "Robotics Engineering",
    "Society, Technology, and Policy",
    "Systems Engineering"
]

# Research interests and topics
interests = [
    "Algorithms & Theory",
    "Artificial Intelligence",
    "Bioinformatics",
    "Biomechanics",
    "Blockchain & Distributed Systems",
    "Cloud Computing",
    "Computer Graphics",
    "Computer Networks",
    "Computer Vision",
    "Cybersecurity",
    "Data Mining",
    "Database Systems",
    "Deep Learning",
    "Digital Signal Processing",
    "Embedded Systems",
    "Environmental Modeling",
    "Game Development",
    "High Performance Computing",
    "Human-Computer Interaction",
    "Human-Robot Interaction",
    "Internet of Things",
    "Machine Learning",
    "Materials Science",
    "Mobile Computing",
    "Natural Language Processing",
    "Operating Systems",
    "Quantum Computing",
    "Robotics",
    "Software Engineering",
    "Sustainable Energy Systems",
    "Virtual Reality & Augmented Reality",
    "Web Technologies"
]

# Programming languages and technologies
languages = [
    "Assembly",
    "C",
    "C#",
    "C++",
    "Dart",
    "Go",
    "Haskell",
    "Java",
    "JavaScript",
    "Julia",
    "Kotlin",
    "MATLAB",
    "Perl",
    "PHP",
    "Python",
    "R",
    "Ruby",
    "Rust",
    "Scala",
    "SQL",
    "Swift",
    "TypeScript",
    "Visual Basic"
]

# WPI Computer Science courses (undergraduate level)
courses = [
    "CS1101",  # Introduction to Program Design
    "CS1102",  # Accelerated Introduction to Program Design
    "CS2011",  # Introduction to Machine Organization and Assembly Language
    "CS2022",  # Discrete Mathematics
    "CS220X",  # Discrete Mathematics for Transfer Students
    "CS2102",  # Object-Oriented Design Concepts
    "CS2119",  # Application Building with Object-Oriented Concepts
    "CS2301",  # Systems Programming for Non-majors
    "CS2303",  # Systems Programming Concepts
    "CS3013",  # Operating Systems
    "CS3041",  # Human-Computer Interaction
    "CS3133",  # Foundations of Computer Science
    "CS3431",  # Database Systems I
    "CS3516",  # Computer Networks
    "CS3733",  # Software Engineering
    "CS4120",  # Analysis of Algorithms
    "CS4123",  # Theory of Computation
    "CS4233",  # Object-Oriented Analysis & Design
    "CS4241",  # Webware: Computational Technology for Network Information Systems
    "CS4341",  # Introduction to Artificial Intelligence
    "CS4342",  # Machine Learning
    "CS4401",  # Software Security Engineering
    "CS4404",  # Tools and Techniques in Computer Network Security
    "CS4432",  # Database Systems II
    "CS4513",  # Distributed Computing Systems
    "CS4514",  # Concurrent Programming
    "CS4516",  # Advanced Computer Networks
    "CS4518",  # Mobile and Ubiquitous Computing
    "CS4533",  # Techniques of Programming Language Translation
    "CS4731",  # Computer Graphics
    "CS4732",  # Computer Animation
    "CS4801",  # Introduction to Cryptography and Communication Security
]

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