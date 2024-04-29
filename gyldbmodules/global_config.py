# 全局配置
# 线上环境需要修改 ADDRESS， run_in_local

ADDRESS = '127.0.0.1:8080'
# 查询执行中的危机值
QUERY_RUNNING_CVS_URL = f'http://{ADDRESS}/gyl/cv/inner_call_running_cvs'
# 处理危机值
HANDLE_CV_URL = f'http://{ADDRESS}/gyl/cv/inner_call_create_cv'

run_in_local = True