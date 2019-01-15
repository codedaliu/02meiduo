from django_redis import get_redis_connection
from rest_framework import serializers

from mall import settings
from oauth.models import OAuthQQUser
from oauth.utils import check_access_token
from users.models import User, Address
from users.utils import generic_verify_url


# class OAuthQQUserSerializer(serializers.Serializer):
#
#     '''
#     qq登陆创建用户用序列化器
#     '''
#     access_token = serializers.CharField(label='操作凭证')
#     mobile = serializers.RegexField(label='手机号',regex='r^1[3-9]\d{9}$')
#     password = serializers.CharField(label='密码', max_length=20, min_length=8)
#     sms_code = serializers.CharField(label='短信验证码')
#
#     def validate(self, attrs):
#
#         #检验access_token mobile password sms_code
#
#         access_token = attrs['access_token']
#         #平身份获取ｏｐｅｎｉｄ
#         openid = check_access_token(access_token)
#
#         if openid is None:
#             raise serializers.ValidationError('openid 错误')
#
#         attrs['openid']=openid
#
#         mobile = attrs.get('mobile')
#         password = attrs['password']
#         attrs_sms_code = attrs.get('sms_code')
#         # 链接ｒｅｄｉｓ
#         from django_redis import get_redis_connection
#         # 获取redis 保存中的验证码
#         redis_conn = get_redis_connection('code')
#         redis_sms = redis_conn.get('sms_' + mobile)
#
#         # 判断验证码是否有值
#         if redis_sms is None:
#             raise serializers.ValidationError('验证码过过期')
#         # 最好删除验证码
#         redis_conn.delete('sms_' + mobile)
#         if redis_sms.decode()!= attrs_sms_code:
#             # if redis_code.decode() != sms_code:
#             raise serializers.ValidationError('验证码错误')
#
#         #对手机号进行判断
#         try:
#             user = User.objects.get(mobile = mobile)
#         except User.DoesNotExist:
#             # 如果没有注册要对用户进行注册
#             pass
#         else:
#             #说明注册过了　需要对密码进行验证
#             if not user.check_password(['password']):
#                 raise serializers.ValidationError('密码错误')
#             attrs['user']=user
#             # attrs["openid"]=openid
#         return attrs
#
#     def create(self, validated_data):
#         user = validated_data['user']
#
#         if user is None:
#             user = User.objects.create(
#                 mobile=validated_data.get('mobile'),
#                 username = validated_data.get('mobile'),
#                 password = validated_data.get('password')
#             )
#             user.set_password((validated_data['password']))
#             user.save()
#
#         qquser = OAuthQQUser.objects.create(
#             user = user,
#             openid = validated_data['openid'],
#         )
#         return qquser


class OAuthQQUserSerializer(serializers.Serializer):

    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')


    # def validate(self, data):
    def validate(self, attrs):

        #1. 需要对加密的openid进行处理
        access_token = attrs.get('access_token')
        print(access_token)
        openid = check_access_token(access_token)

        if openid is None:
            raise serializers.ValidationError('openid错误')

        # 我们通过attrs来传递数据
        attrs['openid']=openid

        #2. 需要对短信进行验证
        # 2.1 获取用户提交的
        mobile = attrs.get('mobile')
        sms_code = attrs['sms_code']
        # 2.2 获取 redis
        redis_conn = get_redis_connection('code')

        redis_code = redis_conn.get('sms_' + mobile)

        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')

        # 最好删除短信
        redis_conn.delete('sms_' + mobile)
        # 2.3 比对
        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码不一致')

        #3. 需要对手机号进行判断
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #说明没有注册过
            #创建用户
            # User.objects.create()
            pass
        else:
            #说明注册过,
            # 注册过需要验证密码
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码不正确')

            attrs['user']=user


        return attrs

    # request.data --> 序列化器(data=xxx)
    # data --> attrs -->validated_data
    def create(self, validated_data):

        user = validated_data.get('user')

        if user is None:
            #创建user
            user = User.objects.create(
                mobile=validated_data.get('mobile'),
                username=validated_data.get('mobile'),
                password=validated_data.get('password')
            )

            #对password进行加密
            user.set_password(validated_data['password'])
            user.save()

        qquser = OAuthQQUser.objects.create(
            user=user,
            openid=validated_data.get('openid')
        )


        return qquser


