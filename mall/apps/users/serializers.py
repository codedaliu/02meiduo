import re

from rest_framework import serializers

from mall import settings
from users.models import User, Address
from users.utils import generic_verify_url


class RegiserUserSerializer(serializers.ModelSerializer):


    #验证手机号　用户名　密码　短信验证码　确认密码　是否同意协议
    #自己定义字段就可以了
    #从前段拿过来的
    sms_code = serializers.CharField(label='短信验证码', max_length=6, min_length=6, write_only=True, required=True,
                                     allow_blank=False)
    allow = serializers.CharField(label='是否同意协议', required=True, allow_null=False, write_only=True)
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False, write_only=True)

    token = serializers.CharField(label='token', read_only=True)

    '''
    ModelSerializer 自动生成字段过程　会对fields进行遍历，先去model中查看是否有相应的字段
    如果有　则自动生成
    如果没有　则查看当前类是否有
    '''
    class Meta:
        model = User
        fields = ['id','token','mobile','username','password','sms_code','allow','password2']

        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self,value):
        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号不符合规则')
        return value

    def validate_allow(self,value):

        if value != 'true':
            raise serializers.ValidationError('没有同意协议')
        return value

    def validate(self, attrs):
        attrs_mobile = attrs.get('mobile')
        attrs_sms_code = attrs.get('sms_code')
        #链接ｒｅｄｉｓ
        from django_redis import get_redis_connection
        #获取redis 保存中的验证码
        redis_conn = get_redis_connection('code')
        redis_sms = redis_conn.get('sms_'+attrs_mobile)

        # 判断验证码是否有值
        if redis_sms is None:
            raise serializers.ValidationError('验证码过过期')
        # 最好删除验证码
        redis_conn.delete('sms_'+attrs_mobile)
        if attrs_sms_code != redis_sms.decode():
            raise serializers.ValidationError('验证码错误')
        password = attrs['password']
        password2 = attrs['password2']

        if password2 !=password:
            raise serializers.ValidationError('两次密码不一致')


        return attrs

    def create(self,validated_data):
        del validated_data['password2']
        del validated_data['allow']
        del validated_data['sms_code']
        user = super().create(validated_data)

        user.set_password(validated_data['password'])
        # user.save()
        user.save()
        #用户入库之后生成token
        from rest_framework.settings import api_settings

        #4.1需要使用ｊｗｔ的两个方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        #4.2让payload 城防一些用户信息
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token=token


        return user


# ==========邮箱发送

class UserCenterInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','username','mobile','email','email_active')


class UserEmailInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','email')
        extra_kwargs = {
            'email':{'required':True}
        }

    def update(self,instance,validated_data):
        #先把数据更新
        email = validated_data.get('email')

        instance.email = email
        instance.save()

        #在发送邮件
        # from django.core.mall import send_mail
        # 主题
        subject = '美多商城激活邮件'
        # 内容
        message = ''
        # 谁发送的
        from_email = settings.EMAIL_FROM
        #收件人列表
        recipient_list = [email]

        verify_url = generic_verify_url(instance.id)
        print('hahaah')

        from celery_tasks.mall.tasks import send_celery_email
        send_celery_email.delay(subject,message,
                                from_email,
                                email,
                                verify_url,
                                recipient_list)
        return instance

class AddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def create(self, validated_data):
        validated_data['user']=self.context['request'].user
        # return Address.objects.create(**validated_data)

        return super().create(validated_data)

    def delete(self,validated_data):
        validated_data['user']=self.context['request'].user
        return super().destroy(validated_data)

