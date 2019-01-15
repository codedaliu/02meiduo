from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from users.views import UserCenterInfoAPIView
from . import views
urlpatterns = [
    #设置用户名函数路由
    url(r'usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameCountAPView.as_view()),
    # 设置获取ｍｏｂｉｌｅ正则和mobile类路由
    url(r'phones/(?P<mobile>1[345789]\d{9})/count/$',views.RegisterPhoneCountAPIView.as_view()),
    url(r'^$',views.RegiserUserAPIView.as_view()),
    # 设置获取ＵＵID生成图片验证码函数
    # url(r'^imagecodes/(?P<image_code_id>.+)/$', views.RegisterImageCodeView.as_view()),
    #用户登陆
    url(r'^auths/$', obtain_jwt_token),
    url(r'^infos/$', views.UserCenterInfoAPIView.as_view()),
    url(r'^emails/$', views.UserEmailInfoAPIView.as_view()),
    url(r'^emails/verification/$', views.UserEmailVerificationAPIView.as_view()),
    url(r'^addresses/$', views.UserAddressAPIView.as_view()),
]
