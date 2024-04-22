from datetime import datetime, timedelta

import requests
import json

from gyldbmodules import global_config
from gyldbmodules.utils.common_utils import run_in_local

is_first_run = True
query_sql = ''
running_ids = {}
systeml = []


"""
从系统中抓取危机值
"""


def read_cv_from_system1():
    global running_ids
    global query_sql
    global is_first_run
    global systeml
    if is_first_run:
        running_ids, query_sql, systeml = get_running_cvs_from_cv_service()
        is_first_run = False
        print('第一次执行，抓取到运行中的危机值: ' + str(running_ids))
        print("query_sql = " + query_sql)

    # 这里的 start_t 不能轻易修改，要保持和 query_sql 中的待替换字段一致
    if run_in_local():
        start_t = str(datetime.now() - timedelta(seconds=6 * 60 * 60))[:19]  # 测试环境 加载前一天未处理的危机值
    else:
        start_t = str(datetime.now() - timedelta(seconds=600))[:19]  # 正式环境 加载前5分钟未处理的危机值
    query_sql = query_sql.replace('{start_t}', start_t)

    if systeml:
        for cv_source in systeml:
            cv_ids = running_ids.get(str(cv_source))
            idrs = f"resultalertid in ({','.join(cv_ids)}) or " if cv_ids else ''
            key = 'idrs_' + str(cv_source)
            query_sql = query_sql.replace(key, idrs)

    param = {
        "type": "orcl_db_read",
        "db_source": "ztorcl",
        "strcol": ["ALERTDT", "RECIEVEDT", "HISCHECKDT", "HISCHECKDT1"],
        "randstr": "XPFDFZDF7193CIONS1PD7XCJ3AD4ORRC",
        "sql": query_sql
    }

    data = []
    if run_in_local():
        try:
            # 发送 POST 请求，将字符串数据传递给 data 参数
            response = requests.post("http://192.168.124.53:6080/int_api", json=param)
            data = response.text
            data = json.loads(data)
            data = data.get('data')
        except Exception as e:
            print('从系统中抓取危机值失败： ' + e.__str__())
    else:
        # 正式环境
        from tools import orcl_db_read
        data = orcl_db_read(param)

    if not data:
        return

    try:
        cvd = {(str(item['RESULTALERTID']) + '_' + str(item['CV_SOURCE'])): item for item in data}
        # 发送 POST 请求，将字符串数据传递给 data 参数
        requests.post(global_config.HANDLE_CV_URL, json={'cvd': cvd})
    except Exception as e:
        print('调用危机值服务接口 ' + global_config.HANDLE_CV_URL + ' 失败, ' + e.__str__())

    # 更新 running ids
    grouped_dict = {}
    for item in data:
        cv_source = item['CV_SOURCE']
        if cv_source not in grouped_dict:
            grouped_dict[cv_source] = []
        grouped_dict[cv_source].append(item['RESULTALERTID'])

    running_ids = grouped_dict


"""
从危机值服务中查询执行中的所有危机值列表
"""


def get_running_cvs_from_cv_service():
    try:
        response = requests.post(global_config.QUERY_RUNNING_CVS_URL)
        data = response.text
        data = json.loads(data)
        data = data.get('data')
        return data.get('running_ids'), data.get('query_sql'), data.get('systeml')
    except Exception as e:
        print('从危机值服务中抓取处理中的危机值失败： ' + e.__str__())
        return []
