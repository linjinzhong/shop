"""celery异步任务"""

from django.conf import settings
from django.core.mail import send_mail
from celery import Celery

# 在任务处理者中开启 Django项目运行配置
import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
# django.setup()


# 创建一个Celery类的实例对象
app = Celery("celery_tasks.tasks", broker="redis://127.0.0.1:6379/1")


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""

    subject = "卓谨商城激活邮件"
    message = ""
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎你成为卓谨商城注册会员</h1>请点击下面连接激活你的账户<br/><a href="http://175.178.152.249:8000/user/active/%s">http://175.178.152.249:8000/user/active/%s</a>' % (username, token, token)

    send_mail(subject, message, sender, receiver, html_message=html_message)
