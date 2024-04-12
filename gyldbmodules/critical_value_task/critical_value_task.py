# from datetime import datetime, timedelta
#
# import requests
# import json
#
# from gyldbmodules import global_config
# from gyldbmodules.utils.common_utils import run_in_local
#
# inspection_system_running_ids = []
# imaging_system_running_ids = []
# is_first_run = True
#
# CV_SOURCE_INSPECTION_SYSTEM = 2
# CV_SOURCE_IMAGING_SYSTEM = 3
#
# """
# 从系统中抓取危机值
# """
#
#
# def read_cv_from_system():
#     global inspection_system_running_ids
#     global imaging_system_running_ids
#     global is_first_run
#     if is_first_run:
#         idl = get_running_cvs_from_cv_service()
#         for id in idl:
#             if int(id.get('cv_source')) == CV_SOURCE_INSPECTION_SYSTEM:
#                 inspection_system_running_ids.append(id.get('cv_id'))
#             if int(id.get('cv_source')) == CV_SOURCE_IMAGING_SYSTEM:
#                 imaging_system_running_ids.append(id.get('cv_id'))
#
#         is_first_run = False
#         print('第一次执行，抓取到运行中的危机值: 检验系统=' + str(inspection_system_running_ids)
#               + ' 影像系统=' + str(imaging_system_running_ids))
#
#     if run_in_local():
#         start_t = str(datetime.now() - timedelta(seconds=6*60*60))[:19]  # 测试环境 加载前一天未处理的危机值
#     else:
#         start_t = str(datetime.now() - timedelta(seconds=600))[:19]    # 正式环境 加载前5分钟未处理的危机值
#
#     # 1. 查询执行中的危机值
#     # 2. 如果不存在执行中的危机值，根据时间来抓取
#     # 3. 根据有效标识，过滤出所有有效的危机值
#     idrsa = f"resultalertid in ({','.join(inspection_system_running_ids)}) or " if inspection_system_running_ids else ''
#     idrsb = f"resultalertid in ({','.join(imaging_system_running_ids)}) or " if imaging_system_running_ids else ''
#
#     # sql = f"""
#     #         select * from inter_lab_resultalert
#     #         where ({idrs} alertdt > to_date('{start_t}', 'yyyy-mm-dd hh24:mi:ss')) and
#     #         VALIDFLAG=1 and HISCHECK1SYNCFLAG =0
#     #         """
#     inspection_system_table = 'inter_lab_resultalert'
#     imaging_system_table = 'NS_EXT.PACS危急值上报表'
#     sql = f"""
#             select a.*, 2 cv_source from {inspection_system_table} a
#             where ({idrsa} alertdt > to_date('{start_t}', 'yyyy-mm-dd hh24:mi:ss')) and VALIDFLAG=1
#             union
#             select b.*, 3 cv_source from {imaging_system_table} b
#             where ({idrsb} alertdt > to_date('{start_t}', 'yyyy-mm-dd hh24:mi:ss')) and VALIDFLAG=1
#             """
#
#     param = {
#         "type": "orcl_db_read",
#         "db_source": "ztorcl",
#         "randstr": "XPFDFZDF7193CIONS1PD7XCJ3AD4ORRC",
#         "sql": sql
#     }
#
#     datetime_param = ['ALERTDT', 'RECIEVEDT', 'HISCHECKDT1', 'HISCHECKDT']
#     data = []
#     if run_in_local():
#         try:
#             # 发送 POST 请求，将字符串数据传递给 data 参数
#             response = requests.post("http://192.168.124.53:6080/int_api", json=param)
#             data = response.text
#             data = json.loads(data)
#             data = data.get('data')
#         except Exception as e:
#             print('从系统中抓取危机值失败： ' + e.__str__())
#     else:
#         # 正式环境
#         from tools import orcl_db_read
#         data = orcl_db_read(param)
#         # # 统一处理时时间格式
#         # if data is not None and len(data) > 0:
#         #     for d in data:
#         #         for p in datetime_param:
#         #             if d[p]:
#         #                 d[p] = d[p].strftime('%Y-%m-%d %H:%M:%S')
#
#     # 从 running cvs 中移除已经处理完成的危机值
#     for item in data:
#         dt = str(item['HISCHECKDT1'])
#         # 回传时间不为空 说明已处理
#         if not dt.isdigit():
#             if item['CV_SOURCE'] == CV_SOURCE_INSPECTION_SYSTEM \
#                     and inspection_system_running_ids.__contains__(item['RESULTALERTID']):
#                 inspection_system_running_ids.remove(item['RESULTALERTID'])
#             if item['CV_SOURCE'] == CV_SOURCE_IMAGING_SYSTEM \
#                     and imaging_system_running_ids.__contains__(item['RESULTALERTID']):
#                 imaging_system_running_ids.remove(item['RESULTALERTID'])
#
#     # 处理检验系统危机值
#     list_a = [d for d in data if d['CV_SOURCE'] == CV_SOURCE_INSPECTION_SYSTEM and str(d['HISCHECKDT1']).isdigit()]
#     if list_a:
#         handle_cv(CV_SOURCE_INSPECTION_SYSTEM, inspection_system_running_ids, list_a)
#     # 处理影像系统危机值
#     list_b = [d for d in data if d['CV_SOURCE'] == CV_SOURCE_IMAGING_SYSTEM and str(d['HISCHECKDT1']).isdigit()]
#     if list_b:
#         handle_cv(CV_SOURCE_IMAGING_SYSTEM, imaging_system_running_ids, list_b)
#
#
# def handle_cv(cv_source, running_ids, data):
#     # 按字典格式将系统危机值存储起来
#     system_cv = {}
#     if data is not None and len(data) > 0:
#         for d in data:
#             system_cv[d.get('RESULTALERTID')] = d
#
#     new_ids = [item['RESULTALERTID'] for item in data]
#
#     del_idl = list(set(running_ids) - set(new_ids))
#     new_idl = list(set(new_ids) - set(running_ids))
#
#     # 作废危机值
#     if del_idl:
#         for del_id in del_idl:
#             running_ids.remove(del_id)
#         param = {
#             'cv_ids': del_idl,
#             'cv_source': cv_source
#         }
#         call_cv_method(global_config.INVALID_CRISIS_VALUE_URL, param)
#
#     # 新增危机值
#     if new_idl:
#         cvs = []
#         for new_id in new_idl:
#             running_ids.append(new_id)
#             cvs.append(system_cv[new_id])
#         param = {
#             'cvs': cvs,
#             'cv_source': cv_source
#         }
#         call_cv_method(global_config.NEW_CREATE_CV_URL, param)
#
#
# """
# 从危机值服务中查询执行中的所有危机值列表
# """
#
#
# def get_running_cvs_from_cv_service():
#     try:
#         response = requests.post(global_config.QUERY_RUNNING_CVS_URL)
#         data = response.text
#         data = json.loads(data)
#         data = data.get('data')
#
#         return data
#     except Exception as e:
#         print('从危机值服务中抓取处理中的危机值失败： ' + e.__str__())
#     return []
#
#
# def call_cv_method(url: str, param):
#     try:
#         # 发送 POST 请求，将字符串数据传递给 data 参数
#         requests.post(url, json=param)
#     except Exception as e:
#         print('调用危机值服务接口 ' + url + ' 失败, param = ' + str(param) + e.__str__())
#
#
#
