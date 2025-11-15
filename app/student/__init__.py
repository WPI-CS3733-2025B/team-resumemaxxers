from flask import Blueprint

student_blueprint = Blueprint('student', __name__)

from app.student import student_routes