from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from mall import settings


def generic_opne_id(openid):
    # 创建一个序列化器　secret_key秘钥
    # expires_in 过期时间　单位是秒
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    # 组织数据
    data = {
        'openid': openid
    }
    # ３．让序列化器对数据进行处理
    token = s.dumps(data)
    return token.decode()

def check_access_token(access_token):
    #创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    #对数据进行解密
    try:
        data = s.loads(access_token)
    except BaseException:
        return None
    # 返回openid  data 就是自己定义的字典
    return data['openid']

def generic_token(user):
    from rest_framework_jwt.settings import api_settings

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token