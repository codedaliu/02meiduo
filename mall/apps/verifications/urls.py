from django.conf.urls import url

import verifications
from verifications import views

urlpatterns = [
    # 设置获取ＵＵID生成图片验证码函数
    url(r'^imagecodes/(?P<image_code_id>.+)/$', views.RegisterImageCodeView.as_view()),
    # 设置获取手机验证码
    url(r'^smscodes/(?P<mobile>1[3-9]\d{9})/$', views.RegisterSMSCodeView.as_view()),

]