from datetime import datetime, timedelta

import requests
import json
from collections import deque

from gyldbmodules import global_config
from gyldbmodules.critical_value_task import critical_value

is_first_run = True
query_sql = ''
running_ids = {}
systeml = []

# 最近
last_100_xuetang_records = deque(maxlen=100)

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
    if global_config.run_in_local:
        start_t = str(datetime.now() - timedelta(seconds=6 * 60 * 60))[:19]  # 测试环境 加载前一天未处理的危机值
    else:
        start_t = str(datetime.now() - timedelta(seconds=600))[:19]  # 正式环境 加载前5分钟未处理的危机值
    query_sql = query_sql.replace('{start_t}', start_t)

    if systeml:
        merged_list = []
        for cv_source in systeml:
            if cv_source == 2:
                cv_ids = running_ids.get(str(cv_source))
                idrs = f"resultalertid in ({','.join(cv_ids)}) or " if cv_ids else ''
                key = 'idrs_' + str(cv_source)
                query_sql = query_sql.replace(key, idrs)
            else:
                cv_ids = running_ids.get(str(cv_source))
                if cv_ids:
                    merged_list = merged_list + cv_ids

        merged_list = [f"'{item}'" for item in merged_list]
        idrs = f"resultalertid in ({','.join(merged_list)}) or " if merged_list else ''
        query_sql = query_sql.replace('idrs_3', idrs)

    param = {
        "type": "orcl_db_read",
        "db_source": "ztorcl",
        "strcol": ["ALERTDT", "RECIEVEDT", "HISCHECKDT", "HISCHECKDT1"],
        "randstr": "XPFDFZDF7193CIONS1PD7XCJ3AD4ORRC",
        "sql": query_sql
    }

    data = []
    if global_config.run_in_local:
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
        # 将 cv_source 转为大写
        data = [
            {("CV_SOURCE" if k == "cv_source" else k): v for k, v in item.items()}
            for item in data
        ]
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


"""
读取最近 5 分钟 床旁血糖危机值
"""


def read_xuetang_cv_and_report():
    data = []
    param = {
        "type": "orcl_db_read",
        "db_source": "nshis",
        "randstr": "XPFDFZDF7193CIONS1PD7XCJ3AD4ORRC",
        "sql": "select a.*, b.姓名, b.年龄, b.性别, b.住院医师, b.出院科室ID as 所属科室ID "
               "from V_XT_BG_TESTRESULT@xuetang a left join 病案主页 b on a.住院号 = b.住院号 and a.住院次数 = b.主页id  "
               "where a.记录时间 >= SYSDATE - INTERVAL '5' MINUTE Order By 记录时间 DESC"
    }
    if global_config.run_in_local:
        try:
            # 发送 POST 请求，将字符串数据传递给 data 参数
            response = requests.post("http://192.168.3.12:6080/int_api", json=param)
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

    new_xuetang = []
    for record in data:
        if record.get('ID') in last_100_xuetang_records:
            continue
        new_xuetang.append(record)

    if not new_xuetang:
        # 不存在新记录 直接返回
        return

    for record in new_xuetang:
        try:
            if '极低' in record.get('危急值'):
                flag = 'LL'
            elif '极高' in record.get('危急值'):
                flag = 'HH'
            else:
                continue

            if not record.get('所属科室ID'):
                print("床旁血糖危机值数据异常，不存在所属科室信息：", record)
                last_100_xuetang_records.append(record.get('ID'))
                continue

            cur_time = datetime.now()
            timer = cur_time.strftime("%Y-%m-%d %H:%M:%S")
            sex = '1'
            if record.get('性别') and '女' in record.get('性别'):
                sex = '2'
            id = record.get('ID')
            dept_id = record.get('所属科室ID')
            if type(dept_id) == float:
                dept_id = str(int(dept_id))
            json_data = {
                "cv_source": 5,
                "RESULTALERTID": id,
                "ALERTMAN": record.get('护士工号'),
                "ALERTDT": timer,
                "REPORTID": id,
                "RESULTID": id,
                "PAT_TYPECODE": '3',
                "PAT_NO": record.get('住院号'),
                "PAT_NAME": record.get('姓名'),
                "PAT_SEX": sex,
                "PAT_AGESTR": record.get('年龄'),
                "REQ_BEDNO": record.get('床号'),
                "REQ_DOCNO": record.get('住院医师'),
                "REQ_DEPTNO": dept_id,
                "REQ_WARDNO": record.get('病区ID'),
                "RPT_ITEMID": id,
                "RPT_ITEMNAME": record.get('项目') + '-' + record.get('测量时段'),
                "RESULT_STR": record.get('测量值'),
                "RESULT_FLAG": flag,
                "RESULT_UNIT": record.get('单位'),
                "VALIDFLAG": '1'
            }
            critical_value.report_cv(json_data)
            last_100_xuetang_records.append(id)
        except Exception as e:
            print("床旁血糖危机值数据异常，上报失败：record = ", record, " json_data = ", json_data, "exception = ", e)
            continue

