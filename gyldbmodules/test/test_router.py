from flask import Blueprint

task = Blueprint('timed task', __name__, url_prefix='/task')


@task.route('/ping', methods=['POST'])
def running_cvs():
    return 'SEVER OK'


