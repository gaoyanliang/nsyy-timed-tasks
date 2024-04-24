from flask import Blueprint

from gyldbmodules.critical_value_task.critical_value_router import cv
from gyldbmodules.test.test_router import task


gylroute = Blueprint('gyl', __name__)

gylroute.register_blueprint(task)

gylroute.register_blueprint(cv)
