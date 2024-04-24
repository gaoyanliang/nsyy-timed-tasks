import json
import traceback

from datetime import datetime
from flask import Blueprint, jsonify, request

from gyldbmodules.critical_value_task import critical_value

cv = Blueprint('critical value', __name__, url_prefix='/cv')


@cv.route('/query_cv', methods=['GET', 'POST'])
def query_cv():
    try:
        json_data = json.loads(request.get_data().decode('utf-8'))
        critical_value.query_cv(int(json_data.get('cv_source')))
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Exception occurred: {traceback.print_exc()}")
    return jsonify({
        'code': 20000
    })


@cv.route('/report_cv', methods=['POST'])
def report_cv():
    try:
        json_data = json.loads(request.get_data().decode('utf-8'))
        critical_value.report_cv(json_data)
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Exception occurred: {traceback.print_exc()}")
    return jsonify({
        'code': 20000
    })


@cv.route('/cancel_cv', methods=['POST'])
def cancel_cv():
    try:
        json_data = json.loads(request.get_data().decode('utf-8'))
        critical_value.cancel_cv(json_data.get('cv_id'), int(json_data.get('cv_source')))
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Exception occurred: {traceback.print_exc()}")
    return jsonify({
        'code': 20000
    })

