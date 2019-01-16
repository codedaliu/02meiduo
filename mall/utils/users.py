import re

from django.contrib.auth.backends import ModelBackend

from users.models import User

#将用户的信息返还给前端保存登陆状态
def jwt_response_payload_handler(token, user=None, request=None):

    return {
        'token': token,
        'user_id':user.id,
        'username':user.username
    }

#对用户登陆的方式判断做一个抽取
def get_user_by_account(username):
    try:
        if re.match(r'1[3-9]\d{9}', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return user


class UsernameMobleModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        #1. 根据用户名确认用户输入的是手机号还是用户名
        # try:
        #     if re.match(r'1[3-9]\d{9}',username):
        #         #手机号
        #         user = User.objects.get(mobile=username)
        #     else:
        #         #用户名
        #         user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     user = None
        user = get_user_by_account(username)
        #2. 验证码用户密码
        if user is not None and user.check_password(password):
            return user
        # 必须返回数据
        return None


# 扩展的
class MyBackend(object):
    def authenticate(self, request, username=None, password=None):
        user = get_user_by_account(username)
        # 2. 验证码用户密码
        if user is not None and user.check_password(password):
            return user
        # 必须返回数据
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


