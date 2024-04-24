from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from gyldbmodules.critical_value_task.cv_task import read_cv_from_system1

timed_task_scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


def add_task():
    # 定时抓取危机值
    timed_task_scheduler.add_job(read_cv_from_system1, trigger='interval',
                                 seconds=30,
                                 max_instances=10)


def schedule_task():
    # run_time = datetime.now()
    run_time = datetime.now() + timedelta(minutes=1)
    timed_task_scheduler.add_job(add_task, 'date', run_date=run_time)
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

