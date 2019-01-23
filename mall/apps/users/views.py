
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from libs.captcha.captcha import captcha
from users.serializers import UserCenterInfoSerializer, UserEmailInfoSerializer, AddressSerializer, \
    AddUserBrowsingHistorySerializer, SKUSerializer, AddressTitleSerializer
from users.models import User
from users.serializers import RegiserUserSerializer
from users.utils import check_token

#判断用户是否存在
class RegisterUsernameCountAPView(APIView):

    '''
    获取用户的个数
    GET /users/username/(?p<username>\w{5,20})/count/

    '''
    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        context = {
            'count':count,
            'username':username,
        }
        return Response(context)


#查询手机号的个数
class RegisterPhoneCountAPIView(APIView):

    def get(self,request,mobile):

        count = User.objects.filter(mobile=mobile).count()
        context = {
            'count':count,
            'phone':mobile,
        }

        return Response(context)

#生成图片验证码
class RegisterImageCodeView(APIView):

    def get(self,request,image_code_id):

        #创建图片和验证码　
        text,image = captcha.generate_captcha()
        #通过redis保存验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,60,text)
        #将图片返回　　注意　图片是　二进制的
        return HttpResponse(image,content_type='image/jpeg')
#用户注册
class RegiserUserAPIView(APIView):

    def post(self,request):
        #１．接收数据
        data = request.data
        #２．校验数据
        serializer = RegiserUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data)

# 用户中心
# 方法一　采用ＡＰＩＶｉｅｗ基类
class UserCerterInfoAPIView(APIView):

    #添加　权限　必须是登陆用户才可以访问
    permission_classes = [IsAuthenticated]

    def get(self,request):
        #获取用户信息

        user = request.user
        #将模型转化字典Ｊｓｏｎ
        serializer = UserCenterInfoSerializer(user)
        #３．返回相应
        return Response(serializer.data)



#用户中心　采用三级视图方法二
class UserCenterInfoAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserCenterInfoSerializer

    #已有父类不能满足我们的需求
    def get_object(self):
        return self.request.user


'''
当用户输入邮箱之后点击保存的时候
１．我们需要将邮箱的内容发送给后端，后端需要更新
指定用户的ｅｍａｉｌ字段
２．同时需要给这个邮箱发送一个　激活链接
３．当用户点击激活链接的时候，改变ｅｍａｉｌ_ａｃｔｉｖｅ的状态


'''

# class UserEmailInfoAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#
#     def put(self,request):
#         #需要接收邮箱
#         data = request.data
#         #校验
#         serializer = UserEmailInfoSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         #更新数据
#         serializer.save()
#
#         #发送邮件
#         # 返回邮件
#         return Response(serializer.data)



from rest_framework.generics import UpdateAPIView
# 向用户发送邮件　方法二
class UserEmailInfoAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmailInfoSerializer
    #父类不能满足我们的需求
    def get_object(self):
        print('laile laile')
        return self.request.user

#验证当前用户的邮件
class UserEmailVerificationAPIView(APIView):

    def get(self,request):
        #1.接收ｔｏｋｅｎ信息
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        #对ｔｏｋｅｎ进行解析
        user_id = check_token(token)

        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(pk=user_id)
        #修改状态
        user.email_active = True
        user.save()

        #返回相应
        return Response({'msg':'ok'})

from rest_framework.generics import CreateAPIView,DestroyAPIView
#新增地址
#新增地址
'''
1.分析需求
２．把需要做的事情写下来
３路由和请求方式
４．确定试图
５．按照步骤实现功能

新增地址

１．后端接收数据
２．对数据进行校验
３．数据入库
４．返回相应'''

class AddressViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    """
    用户地址新增与修改
    list GET: /users/addresses/
    create POST: /users/addresses/
    destroy DELETE: /users/addresses/
    action PUT: /users/addresses/pk/status/
    action PUT: /users/addresses/pk/title/
    """

    #制定序列化器
    serializer_class = AddressSerializer
    #添加用户权限
    permission_classes = [IsAuthenticated]
    #由于用户的地址有存在删除的状态,所以我们需要对数据进行筛选
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        count = request.user.addresses.count()
        if count >= 20:
            return Response({'message':'保存地址数量已经达到上限'},status=status.HTTP_400_BAD_REQUEST)

        return super().create(request,*args,**kwargs)

    def list(self, request, *args, **kwargs):
        """
        获取用户地址列表
        """
        # 获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        # 响应
        return Response({
            'user_id': user.id,
            # 'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

#删除地址
# class UseraAddressAPIView()


from rest_framework.generics import CreateAPIView
class UserHistoryAPIVIew(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer = AddUserBrowsingHistorySerializer


from rest_framework import mixins
from rest_framework.generics import GenericAPIView


class UserBrowsingHistoryView(mixins.CreateModelMixin, GenericAPIView):
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def post(self,request):
        return self.create(request)

    def get(self,request):
        #获取用户user_id
        user_id = request.user.id
        #链接ｒｅｄｉｓ
        redis_conn = get_redis_connection('history')
        #获取数据
        history_sku_ids = redis_conn.lrange('hsitory_%s'%user_id,0,5)
        skus = []
        for sku_id in history_sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            skus.append((sku))

        #实现序列化器
        serializers = SKUSerializer(skus,many=True)

        return Response(serializers.data)


from rest_framework_jwt.views import ObtainJSONWebToken
class MergeLoginAPVIiew(ObtainJSONWebToken):


    def post(self,request,*args,**kwargs):

        response = super().post(request)

        #如果用户登录成功 进行数据合并
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            #表示用户登录成功
            user = serializer.validated_data.get('user')
            #合并购物车
        return response








