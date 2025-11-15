from flask import Blueprint

faculty_blueprint = Blueprint('faculty', __name__)

from app.faculty import faculty_routes