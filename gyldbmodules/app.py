from flask import Blueprint

from gyldbmodules.test.test_router import task


gylroute = Blueprint('gyl', __name__)

gylroute.register_blueprint(task)
