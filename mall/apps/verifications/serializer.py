
from rest_framework import serializers
from django_redis import get_redis_connection

#定义序列化器　用以校验生成的数据
from utils.exceptions import logger


class RegisterSMSCodeSerializer(serializers.Serializer):
        text = serializers.CharField(label='用户输入验证码ｉｄ',max_length=4,min_length=4,required=True)
        image_code_id = serializers.UUIDField(label='验证码唯一性')

        def validate(self,attrs):
            #获取用户提交的验证码
            text = attrs['text']
            image_code_id = attrs['image_code_id']
            print(image_code_id)

            #获取ｒｅｄｉｓ中储存的信息
            # ＃链接ｒｅｄｉｓ
            redis_conn = get_redis_connection('code')
            # image_id = redis_conn.get('image_code_id')
            print(image_code_id)
            redis_text = redis_conn.get('img_'+str(image_code_id))
            print(redis_text)
            #判断redis_text 是否存在
            if redis_text is None:
                raise serializers.ValidationError('验证码已经过期')
            #将ｒｅｄｉｓ中的验证码删除
            # try:
            #     redis_conn.delete('image_'+image_code_id)
            # except Exception as e:
            #     logger.error(e)
            #判断用户输入的验证码和redis 中的是否一致
            if redis_text.decode().lower() != text.lower():
                raise serializers.ValidationError('验证码错误')

            return attrs



