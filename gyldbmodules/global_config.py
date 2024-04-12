# 全局配置

ADDRESS = '127.0.0.1:8080'
# 查询执行中的危机值
QUERY_RUNNING_CVS_URL = f'http://{ADDRESS}/gyl/cv/inner_call_running_cvs'
# 处理危机值
HANDLE_CV_URL = f'http://{ADDRESS}/gyl/cv/inner_call_create_cv1'

# # 新建危机值
# NEW_CREATE_CV_URL = f'http://{ADDRESS}/gyl/cv/inner_call_create_cv'
# # 作废危机值
# INVALID_CRISIS_VALUE_URL = f'http://{ADDRESS}/gyl/cv/inner_call_invalid_cv'
