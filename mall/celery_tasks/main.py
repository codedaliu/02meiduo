import os

from celery import Celery

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mall.settings")
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'
#创建ｃｅｌｅｒｙ案例
# main 习惯添加　celery文件路径
app = Celery(main='celery_tasks')

#设置broker
app.config_from_object('celery_tasks.config')

#让ｃｅｌｅｒｙ自己检测
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.mall'])

#让worker执行人物
# celery -A celery_tasks.main worker -l info