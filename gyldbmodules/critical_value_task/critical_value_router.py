import json
import traceback

from datetime import datetime
from flask import Blueprint, jsonify, request

from gyldbmodules.critical_value_task import critical_value

cv = Blueprint('critical value', __name__, url_prefix='/cv')


@cv.route('/query_cvl_by_source', methods=['GET', 'POST'])
def query_cvl_by_source():
    try:
        json_data = json.loads(request.get_data().decode('utf-8'))
        cv_source = json_data.get('cv_source')
        page_number = json_data.get('page_number')
        page_size = json_data.get('page_size')
        if not cv_source or not page_size or not page_number:
            return jsonify({
                'code': 50000,
                'res': 'cv_source, page_size, page_number can not be nil'
            })
        cvl, total = critical_value.query_cvl_by_source(json_data)
    except Exception:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Exception occurred: {traceback.print_exc()}")
    return jsonify({
        'code': 20000,
        'data': {
            'cvl': cvl,
            'total': total
        }
    })


@cv.route('/report_cv', methods=['POST'])
def report_cv():
    try:
        json_data = json.loads(request.get_data().decode('utf-8'))
        critical_value.report_cv(json_data)
    except Exception:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] Exception occurred: {traceback.print_exc()}"
        print(msg)
        return jsonify({
            'code': 50000,
            'res': msg
        })
    return jsonify({
        'code': 20000
    })


@cv.route('/manual_report_cv', methods=['POST'])
def manual_report_cv():
    try:
        json_data = json.loads(request.get_data().decode('utf-8'))
        critical_value.report_cv(json_data)
    except Exception:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] Exception occurred: {traceback.print_exc()}"
        print(msg)
        return jsonify({
            'code': 50000,
            'res': msg
        })
    return jsonify({
        'code': 20000
    })


@cv.route('/cancel_cv', methods=['POST'])
def cancel_cv():
    try:
        json_data = json.loads(request.get_data().decode('utf-8'))
        critical_value.cancel_cv(json_data.get('cv_id'), int(json_data.get('cv_source')))
    except Exception:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] Exception occurred: {traceback.print_exc()}"
        print(msg)
        return jsonify({
            'code': 50000,
            'res': msg
        })
    return jsonify({
        'code': 20000
    })

