from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from gyldbmodules.critical_value_task.cv_task import read_cv_from_system1, read_xuetang_cv_and_report

timed_task_scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


def add_task():
    # 定时抓取危机值
    timed_task_scheduler.add_job(read_cv_from_system1, trigger='interval',
                                 seconds=30,
                                 max_instances=10)


def add_xuetang_cv_task():
    timed_task_scheduler.add_job(read_xuetang_cv_and_report, trigger='interval',
                                 seconds=55,
                                 max_instances=10)


def schedule_task():
    # run_time = datetime.now() + timedelta(seconds=10)
    run_time = datetime.now() + timedelta(seconds=30)
    timed_task_scheduler.add_job(add_task, 'date', run_date=run_time)

    run_time = datetime.now() + timedelta(seconds=40)
    timed_task_scheduler.add_job(add_xuetang_cv_task, 'date', run_date=run_time)
    # Start the scheduler
    timed_task_scheduler.start()


# try:
#     # 保持主线程运行，否则程序会退出
#     print('开始执行定时任务')
#     schedule_task()
#     while True:
#         time.sleep(2)
# except KeyboardInterrupt:
#     # 如果收到键盘中断信号，则停止调度器
#     timed_task_scheduler.shutdown()

