# from datetime import datetime
#
#
# data = [{'ID': '1721213777987', '患者ID': '22759', '住院号': '13674', '住院次数': '2', '项目': '电脑血糖监测', '医嘱号': 0, '科室ID': '281', '科室名称': '康复科三病区一组', '病区ID': '281', '病区名称': '康复科三病区一组', '床号': '63', '测量时段': '午餐后', '采集时间': '2024-07-16 14:01:00', '测量值': '外出', '测量结果数值': 0, '单位': 'mmol/L', '护士工号': '1801', '护士名字': '何露', '危急值': 0, '测量设备SN': 0, '记录时间': '2024-07-17 18:56:30', '姓名': 0, '年龄': 0, '性别': 0, '住院医师': 0, '所属科室ID': 0}]
#
# for record in data:
#     try:
#         if '极低' in str(record.get('危急值')):
#             flag = 'LL'
#         elif '极高' in str(record.get('危急值')):
#             flag = 'HH'
#         else:
#             continue
#
#         cur_time = datetime.now()
#         timer = cur_time.strftime("%Y-%m-%d %H:%M:%S")
#         sex = '1'
#         if record.get('性别') and '女' in record.get('性别'):
#             sex = '2'
#         id = record.get('ID')
#         dept_id = record.get('所属科室ID')
#         if type(dept_id) == float:
#             dept_id = str(int(dept_id))
#         json_data = {
#             "cv_source": 5,
#             "RESULTALERTID": id,
#             "ALERTMAN": record.get('护士工号'),
#             "ALERTDT": timer,
#             "REPORTID": id,
#             "RESULTID": id,
#             "PAT_TYPECODE": '3',
#             "PAT_NO": record.get('住院号'),
#             "PAT_NAME": record.get('姓名'),
#             "PAT_SEX": sex,
#             "PAT_AGESTR": record.get('年龄'),
#             "REQ_BEDNO": record.get('床号'),
#             "REQ_DOCNO": record.get('住院医师'),
#             "REQ_DEPTNO": dept_id,
#             "REQ_WARDNO": record.get('病区ID'),
#             "RPT_ITEMID": id,
#             "RPT_ITEMNAME": record.get('项目') + '-' + record.get('测量时段'),
#             "RESULT_STR": record.get('测量值'),
#             "RESULT_FLAG": flag,
#             "RESULT_UNIT": record.get('单位'),
#             "VALIDFLAG": '1'
#         }
#         print('成功')
#         # critical_value.report_cv(json_data)
#         # last_100_xuetang_records.append(id)
#     except Exception as e:
#         print("床旁血糖危机值数据异常，上报失败：record = ", record, "exception = ", e)
#         # last_100_xuetang_records.append(record.get('ID'))
#
#
#
#
#
#
#
#
#
#
#
#
