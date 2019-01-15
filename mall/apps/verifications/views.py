from random import randint

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP

#生成图片验证码
from verifications.serializer import RegisterSMSCodeSerializer


class RegisterImageCodeView(APIView):

    def get(self,request,image_code_id):

        #创建图片和验证码　
        text,image = captcha.generate_captcha()
        #通过redis保存验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,600,text)
        #将图片返回　　注意　图片是　二进制的
        return HttpResponse(image,content_type='image/jpeg')


#获取手机短信验证码
class RegisterSMSCodeView(APIView):
    '''
    思路；
    创建序列化器　定义text 和image_ocde_id
    redis 判断该用户是否频繁获取
    生成短信验证码
    ｒｅｄｉｓ　增加记录
    发送短信
    返回相应

    '''
    def get(self,request,mobile):
        params = request.query_params
        print(params)
        serializer = RegisterSMSCodeSerializer(data=params)
        serializer.is_valid(raise_exception=True)

        #链接redis
        redis_conn = get_redis_connection('code')
        #判断用户是否频繁获取
        if redis_conn.get('sms_%s'%mobile):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        #生成短信验证码
        sms_code = '%06d'%randint(0,999999)
        #redis 增加记录
        redis_conn.setex('sms_%s' % mobile, 5 * 60, sms_code)

        # 发送短信
        # ccp = CCP()
        # ccp.send_template_sms(mobile,[sms_code,5],1)
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code)
        return Response({'message':'ok'})