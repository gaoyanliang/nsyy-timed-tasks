import cx_Oracle
import os
from datetime import datetime

# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.AL32UTF8'


def query_cvl_by_source(json_data):
    try:
        connection = cx_Oracle.connect("system", "d67v7rbZyV", "192.168.3.240:1521/orcl")
        cursor = connection.cursor()
        cv_source = int(json_data.get('cv_source'))
        page_number = int(json_data.get('page_number'))
        page_size = int(json_data.get('page_size'))
        start_time = json_data.get('start_time')
        end_time = json_data.get('end_time')

        time_sql = ''
        if start_time and end_time:
            time_sql = f'AND ALERTDT BETWEEN TO_DATE(\'{start_time}\', \'YYYY_MM_DD HH24:MI:SS\')  AND TO_DATE(\'{end_time}\', \'YYYY_MM_DD HH24:MI:SS\')'

        # NS_EXT.PACS危急值上报表   inter_lab_resultalert
        cursor.execute(f"""
            SELECT * from NS_EXT.PACS危急值上报表
            WHERE "cv_source" = {cv_source} {time_sql}
        """)
        retl = cursor.fetchall()
        total = len(retl) if retl else 0

        cursor.execute(f'SELECT * from NS_EXT.PACS危急值上报表 WHERE "cv_source" = {cv_source} {time_sql} ')
        results = cursor.fetchall()
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        results = results[start_index:end_index]

        columns = [desc[0] for desc in cursor.description]
        results_with_columns = []
        for row in results:
            resultd = dict(zip(columns, row))
            results_with_columns.append(resultd)

        return results_with_columns, total
    except Exception as error:
        # 如果出现数据库错误，则执行此处的代码块
        print("数据库错误:", error)
    finally:
        # 无论是否发生异常，都会执行此处的代码块
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def report_cv(json_data):
    try:
        # 连接数据库
        connection = cx_Oracle.connect("system", "d67v7rbZyV", "192.168.3.240:1521/orcl")
        # 创建游标
        cursor = connection.cursor()

        fields = ",".join(json_data.keys())
        fields = fields.replace('cv_source', '\"cv_source\"')
        #placeholders = ":" + ",:".join(json_data.keys())
        values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in json_data.values()])
        sql = f"INSERT INTO NS_EXT.PACS危急值上报表 ({fields}) VALUES ({values})"

        sql = sql.replace('\''+json_data['ALERTDT']+'\'', 'TO_DATE(\'' + json_data['ALERTDT'] + '\', \'YYYY-MM-DD HH24:MI:SS\')')
        # 执行插入操作
        cursor.execute(sql)
        # 提交事务
        connection.commit()
    except cx_Oracle.Error as error:
        # 如果出现数据库错误，则执行此处的代码块
        print("有问题的sql: ", sql)
        raise Exception("数据库错误:", error)
    finally:
        # 无论是否发生异常，都会执行此处的代码块
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


"""
手工上报危机值
"""


def manual_report_cv(json_data):
    json_data['cv_source'] = 0
    # 手工上报的危机值用 时间戳代替
    json_data['RESULTALERTID'] = int(datetime.now().timestamp() * 1000)
    json_data['ALERTDT'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    json_data['VALIDFLAG'] = '1'

    report_cv(json_data)



"""
作废危机值
"""


def cancel_cv(cv_id, cv_source):
    try:
        # 连接数据库
        connection = cx_Oracle.connect("system", "d67v7rbZyV", "192.168.3.240:1521/orcl")
        # 创建游标
        cursor = connection.cursor()

        # 构建更新语句
        sql = f"UPDATE NS_EXT.PACS危急值上报表 SET VALIDFLAG = 0 WHERE RESULTALERTID = \'{cv_id}\' and \"cv_source\" = {cv_source}"

        # 执行插入操作
        cursor.execute(sql)
        # 提交事务
        connection.commit()
    except cx_Oracle.Error as error:
        # 如果出现数据库错误，则执行此处的代码块
        print("有问题的sql: ", sql)
        print("数据库错误:", error)
    finally:
        # 无论是否发生异常，都会执行此处的代码块
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
