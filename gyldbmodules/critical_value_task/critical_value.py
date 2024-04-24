import cx_Oracle


def query_cv(cv_source):
    try:
        # 连接数据库
        connection = cx_Oracle.connect("system", "d67v7rbZyV", "192.168.3.240:1526/orcl")
        # 创建游标
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM NS_EXT.PACS危急值上报表 ")
        for row in cursor:
            print(row)
    except cx_Oracle.Error as error:
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
        connection = cx_Oracle.connect("system", "d67v7rbZyV", "192.168.3.240:1526/orcl")
        # 创建游标
        cursor = connection.cursor()

        fields = ",".join(json_data.keys())
        placeholders = ":" + ",:".join(json_data.keys())
        sql = f"INSERT INTO NS_EXT.PACS危急值上报表 ({fields}) VALUES ({placeholders})"

        # 执行插入操作
        cursor.execute(sql, json_data)
        # 提交事务
        connection.commit()
    except cx_Oracle.Error as error:
        # 如果出现数据库错误，则执行此处的代码块
        print("数据库错误:", error)
    finally:
        # 无论是否发生异常，都会执行此处的代码块
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


"""
作废危机值
"""


def cancel_cv(cv_id, cv_source):
    try:
        # 连接数据库
        connection = cx_Oracle.connect("system", "d67v7rbZyV", "192.168.3.240:1526/orcl")
        # 创建游标
        cursor = connection.cursor()

        # 构建更新语句
        sql = f"UPDATE NS_EXT.PACS危急值上报表 SET VALIDFLAG = 0 WHERE RESULTALERTID = {cv_id} and cv_source = {cv_source}"

        # 执行插入操作
        cursor.execute(sql)
        # 提交事务
        connection.commit()
    except cx_Oracle.Error as error:
        # 如果出现数据库错误，则执行此处的代码块
        print("数据库错误:", error)
    finally:
        # 无论是否发生异常，都会执行此处的代码块
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
