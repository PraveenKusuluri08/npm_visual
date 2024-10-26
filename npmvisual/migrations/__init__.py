from flask import Blueprint

bp = Blueprint("migrations", __name__)

from npmvisual.migrations import main
