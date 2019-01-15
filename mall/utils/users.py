import re

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
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user


# 实现用户登陆（用户名手机号均可登陆的方式）
class UsernameMobleModelBackend():
    def authenticate(self,request,username=None,password=None,**kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
        return None


