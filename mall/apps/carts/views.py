# import base64
# import pickle
#
# from django.shortcuts import render
#
# # Create your views here.
# from rest_framework.response import Response
#
# from rest_framework.views import APIView
#
# from carts.serializers import CartSerializer
# from django_redis import get_redis_connection
#
# class CartAPIView(APIView):
#     '''
#     psot 新增购物车
#     ｇｅｔ　获取购物车
#     ｐｕｔ　修改购物车
#     ｄｅｌｅｔｅ　删除购物车
#
#     '''
#     def perform_authentication(self, request):
#         pass
#
#     def post(self,request):
#         #接受数据
#         data = request.data
#         #校验数据　商品是否存在　商品的个数是否足够
#         serializer = CartSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         #获取校验之后的数据 sku_id count selected
#         #3.获取校验数据之后的数据
#         sku_id = serializer.validated_data.get('sku_id')
#         count = serializer.validated_data['count']
#         selected = serializer.validated_data['selected']
#         #4.获取用户信息
#         try:
#             user = request.user
#         except Exception as e:
#             user = None
#         #5.根据用户的信息进行判断用户是否登录
#         # request.user.is_authenticated
#         if user is not None and user.is_authenticated:
#             #6.登录用户保存在ｒｅｄｉｓ
#             # 6.1链接ｒｅｄｉｓ
#             redis_conn = get_redis_connection('cart')
#             #6.2将数据保存在redis中的ｈａｓｈ和ｓｅｔ中
#             redis_conn.hset('cart_%s'%user.id,sku_id,count)
#
#             if selected:
#                 redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
#                 #返回响应
#                 return Response(serializer.data)
#         else:
#             #7.未登录用户保存在cookie中
#             # 7.1现货取cookie数据
#             cookie_str = request.COOKIES.get('cart')
#             #7.2判断是否存在ｃｏｏｋｉｅ数据
#             if cookie_str is not None:
#                 #说明有数据
#                 #对base64数据进行解码
#                 decode = base64.b64decode(cookie_str)
#                 #将二进制转化为字典
#                 cookie_cart = pickle.loads(decode)
#             else:
#                 #说明没有数据
#                 cookie_cart = {}
#         # 7.3如果添加的购物车商品ｉｄ存在则进行商品商品数量的累加
#         # cookie_cart = {sku_id:{count:xxx}}
#             if sku_id in cookie_cart:
#                 #存在
#                 origin_count = cookie_cart[sku_id]['count']
#                 #出现个数
#                 count += origin_count
#             #7.4如果添加的购物车不存在则直接添加商品信息
#             cookie_cart[sku_id]={'count':count,
#                                      'selected':selected}
#
#             #7.5对字典进行处理
#             # 7.5.1将字典转化为二进制
#             dumps = pickle.dumps(cookie_cart)
#             #7.52 进行base64的编码
#             encode = base64.b64encode(dumps)
#             #将ｂｙｔｅｓ转化为str
#             value = encode.decode()
#             #返回响应
#             response = Response(serializer.data)
#             response.set_cookie('cart',value)
#             return response
"""
当用户点击购物车列表的时候前端需要发送一个getq请求
get 请求的数据　需要激昂用户信息传递过来

1.接受用户信息
2.根据用户信息进行判断
3.登录用户从ｒｅｄｉｓ中获取数据
    3.1链接ｒｅｄｉｓ
    3.2ｈａｓｈ　cart_userid:{sku_id:count}
    set  cart_selected_userid:sku_id
    获取ｈａｓｈ的所有数据
    [sku_id,sku_id]
    3.3根据商品id获取商品详细信息
    3.4返回响应＇
4.从未登录用户从cookie中获取数据
    4.1先从cookie中获取数据
    4.2判断是否存在购物车的数据
    ｛sku_id:{count:xxx}}
    [sku_id,sku_id]
5.根据商品ｉｄ获取商品的详细信息
6.返回响应
"""
import base64
import pickle

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from .serializers import CartSerializer, CartSKUSerializer, CartDeleteSerialzier
from django_redis import get_redis_connection
class CartAPIView(APIView):
    '''
    post 新增购物车
    get　获取购物车数据
    put 修改购物车
    delete 删除购购物车
    '''
    '''
    我们的token 过期了或者被篡改了，就不能添加到购物车了
    正确的业务逻辑是　先让用户添加到购物车
    ｔｏｋｅｎ 过期了就认为是未登录用户
    如果我们要让用户加入到购物车　就不应该先验证用户的ｔｏｋｅｎ

    重写perform_authentication方法
    这样就可以直接进入到　我们的购物车添加的逻辑中来了
    当我们需要验证的时候　再去验证
    '''
    def perform_authentication(self, request):
        pass

    def post(self,request):
        '''
        添加购物车的业务逻辑
        点击用户　添加购物车按钮的时候　前端需要手收集数据
        商品ＩＤ　个数　选中的状态默认为Ture 用户信息
        1.接受数据
        2.校验数据
        3.获取校验之后的数据
        4.获取用户信息
        5.根据用户的信息进行判断用户是否登录
        6.登录用户保存在ｒｅｄｉｓ中
            链接ｒｅｄｉｓ
            将数据保存在ｒｅｄｉｓ中
            返回响应
        7.未登录用户保存在ｃｏｏｋｉｅ中
            7.1先获取ｃｏｏｋｉｅ数据
            7.2判断是否存在cookie数据
            7.3如果添加的购物车商品ｉｄ存在则进行商品数据数量的累加
            7.4如果添加的购物车商品ｉｄ不存在则直接添加爱商品信息
            7.5返回

        :param request:
        :return:
        '''
        # 添加购物车的业务逻辑
        # 点击用户　添加购物车按钮的时候　前端需要手收集数据
        # 商品ＩＤ　个数　选中的状态默认为Ture 用户信息
        # 1.接受数据
        data = request.data

        # 2.校验数据
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # 3.获取校验之后的数据
        count = serializer.validated_data['count']
        sku_id = serializer.validated_data['sku_id']
        selected = serializer.validated_data['selected']

        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
            # request.user.is_authenticated
        # 5.根据用户的信息进行判断用户是否登录(已登陆的)
        if user is not None and user.is_authenticated:
            # 6.登录用户保存在ｒｅｄｉｓ中
            #     链接ｒｅｄｉｓ
            redis_conn = get_redis_connection('cart')
            # #     将数据保存在ｒｅｄｉｓ中
            # #     redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # redis_conn.hincrby('cart_%s'%user.id,sku_id,count)
            # if selected:
            #     redis_conn.sadd('cart_selected_%s'%user.id,sku_id)

            #使用管道将数据保存到redis
            #创建管道
            pl = redis_conn.pipeline()
            #将指令添加到管道中
            pl.hincrby('cart_%s'%user.id,sku_id,count)
            if selected:
                pl.sadd('cart_selected_%s'%user.id,sku_id)
            #执行
            pl.execute()
            #     返回响应
            return Response(serializer.data)
            # 7.未登录用户保存在ｃｏｏｋｉｅ中
        else:

            #     7.1先获取ｃｏｏｋｉｅ数据
            #cookie_info是一个字典
            cookie_info = request.COOKIES.get('cart')

            #     7.2判断是否存在cookie数据
            if cookie_info is not None:
                #说明是有数据 进行解码
                decode = base64.b64decode(cookie_info)
                #将二进制数据转化为字符串
                cookie_cart = pickle.loads(decode)
            else:
                #说明没有数据　进行初始化
                cookie_cart = {}

            #     7.3如果添加的购物车商品ｉｄ存在则进行商品数据数量的累加
            if sku_id in cookie_cart:
                origin_count = cookie_cart[sku_id]['count']

                count += origin_count

            #7.4如果添加的购物车商品ｉｄ不存在则直接添加爱商品信息
            cookie_cart[sku_id]={'count':count,
                                 'selected':selected}
            #7.5对字典进行处理
            #将字典转化未二进制类型
            dump = pickle.dumps(cookie_cart)
            # 7.5.2解码成字符串，进行ｂａｓｅ64编码
            value = base64.b64encode(dump).decode()

        #     7.5返回
            response = Response(serializer.data)
            response.set_cookie('cart',value)
            return response

    #第一遍的get显示购物车的方法
    # def get(self,request):
    #
    #     # 当用户点击购物车列表的时候前端需要发送一个getq请求
    #     data = request.query_params    # get 请求的数据　需要激昂用户信息传递过来
    #     # 1.接受用户信息
    #     try:
    #         user = request.user
    #     except Exception as e:
    #         user = None
    #
    #     # 2.根据用户信息进行判断
    #     if user is not None:
    #     # 3.登录用户从ｒｅｄｉｓ中获取数据
    #     #     3.1链接ｒｅｄｉｓ
    #         redis_conn = get_redis_connection('cart')
    #
    #     #3.2ｈａｓｈ　cart_userid:{sku_id:count}
    #     #set  cart_selected_userid:sku_id
    #     #获取ｈａｓｈ的所有数据
    #         #获取当前用户购物车中的所有商品 从redis中获取的商品是二进制的
    #         redis_user_cart = redis_conn.hgetall('cart_%s'%user.id)
    #         # 获取当前用户购物车中的所有商品的状态
    #         redis_user_selected = redis_conn.smembers('cart_selected_%s'%user.id)
    #         cart = {}
    #         #redis 数据库list类型获取出来的信息是[sku_id,sku_id]
    #         for sku_id,count in redis_user_cart.items():
    #             #二进制的数字可以直接转化成数字类型
    #             #{sku_id:{count:xxx,selected:xxx}}
    #             cart[int(sku_id)] = {
    #                 'count':int(count),
    #                 'selected':sku_id in redis_user_selected
    #             }
    #
    #
    #     #未登录用户从cookie中＇获取数据
    #     else:
    #         cart_str = request.COOKIES.get('cart')
    #         # {sku_id:{count:xxx,selected:xxx}}
    #         if cart_str is not None:
    #             #对获取到的cookie数据进行解码
    #             load = base64.b64decode(cart_str)
    #             #对解码后的二进制数据进行转为字符串
    #             cart = pickle.loads(load)
    #
    #         else:
    #             cart = {}
    #     #获取所有商品的信息  cart.keys()是获取所保存的商品ｉｄ
    #     skus = SKU.objects.filter(id__in=cart.keys())
    #     #对获取到的用户所保存的商品进行遍历将商品数量和勾选状态添加到单条数据上去
    #     #3.3根据商品id获取商品详细信息
    #
    #     for sku in skus:
    #         sku.count = cart[sku.id]['count']
    #         sku.selected = cart[sku.id]['selected']
    #     serializer = CartSKUSerializer(skus,many=True)
    #     #返回响应
    #     return Response(serializer.data)
    #
    #     #3.4返回响应＇
    #     # 4.从未登录用户从cookie中获取数据
    #     #     4.1先从cookie中获取数据
    #     #     4.2判断是否存在购物车的数据
    #     #     ｛sku_id:{count:xxx}}
    #     #     [sku_id,sku_id]
    #     # 5.根据商品ｉｄ获取商品的详细信息
    #     # 6.返回响应

    #查询购物车
    #获取购物车
    def get(self,request):
        # 当用户点击购物车列表的时候前端需要发送一个getq请求
        # get 请求的数据　需要激昂用户信息传递过来
        # 1.接受用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 2.根据用户信息进行判断
        if user is not None:
            # 3.登录用户从ｒｅｄｉｓ中获取数据
            #     3.1链接ｒｅｄｉｓ
            redis_conn = get_redis_connection('cart')
            #     3.2ｈａｓｈ　cart_userid:{sku_id:count}
            #     获取ｈａｓｈ的所有数据
            #     [sku_id,sku_id]
            redis_user_info = redis_conn.hgetall('cart_%s'%user.id)
            #     set  cart_selected_userid:sku_id
            redis_user_selected = redis_conn.smembers('cart_selected_%s'%user.id)
            cart = {}
            for sku_id,count in redis_user_info.items():
                cart[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in redis_user_selected
                    }

            #     3.3根据商品id获取商品详细信息
            #     3.4返回响应＇

        else:
            # 4.从未登录用户从cookie中获取数据
            #     4.1先从cookie中获取数据
            cookie_info = request.COOKIES.get('cart')
            #     4.2判断是否存在购物车的数据
            if cookie_info is not None:
                #将获取出来的数据进行解码
                cart = pickle.loads(base64.b64decode(cookie_info))
            else:
                cart = {}


        # 5.根据商品ｉｄ获取商品的详细信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        # 6.返回响应
        serializer = CartSKUSerializer(instance=skus, many=True)

        return Response(serializer.data)

    #修改购物车信息
    def put(self,request):
        ''''
        1.接受数据
        2.校验数据
        3.获取校验后的数据
        4.判断用户是否登录
        5.根据登录状态进行判断
        6.登录用户redis
            6.1链接redis
            6.2更新redis的数据
            6.3返回响应
        7.未登录用户cookie
            7.1获取Cookie中的数据
            7.1.1判断获取的信息是否存在
            7.2更新cookie
            7.3返回cookie

        '''

        # 1.接受数据
        data = request.data
        # 2.校验数据
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取校验后的数据
        sku_id=serializer.validated_data['sku_id']
        count=serializer.validated_data['count']
        selected=serializer.validated_data['selected']
        # 4.判断用户是否登录
        try:
            user = request.user
        except Exception as e:
            user = None

        # 5.根据登录状态进行判断
        if user is not None:

            # 6.登录用户redis
            #     6.1链接redis
            redis_conn = get_redis_connection('cart')
            #     6.2更新redis的数据
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            else:
                redis_conn.srem('cart_selected_%s'%user.id,sku_id)
            #     6.3返回响应
            return Response(serializer.data)
        else:

            # 7.未登录用户cookie
            cookie_info = request.COOKIES['cart']
            #     7.1获取Cookie中的数据
            #     7.1.1判断获取的信息是否存在
            if cookie_info is not None:
                cart = pickle.loads(base64.b64decode(cookie_info))
            else:
                cart = {}
            #     7.2更新cookie

            if sku_id in cart:
                cart[sku_id]={'count':count,
                              'selected':selected}

            #     7.3返回cookie
            response = Response(serializer.data)
            print(cart)
            value = base64.b64encode(pickle.dumps(cart)).decode()

            response.set_cookie('cart',value)

            return response


    def delete(self,request):
        '''
        1.获取数据
        2.校验数据
        3.获取校验后的数据
        4.获取用户
        5.根据用户信息判断
        6.登录用户redis
            6.1链接redis
            6.2删除数据
            6.3返回响应
        7．未登录用户cookie
            7.1获取cookie中的数据
            7.2删除数据
            7.3返回响应

        '''
        # 1.后端接收数据
        data = request.data
        # 2.校验数据
        serializer = CartDeleteSerialzier(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取校验之后的数据
        sku_id = serializer.validated_data.get('sku_id')
        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5.根据用户信息进行判断
        if user is not None and user.is_authenticated:

            # 6.登陆用户redis
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            #创建管道
            pl = redis_conn.pipeline
            #创建任务
            pl.hdel('cart_%s'%user.id,sku_id)
            pl.srem('cart_selected_%s'%user.id,sku_id)
            #执行
            pl.execute
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:

            # 7.未登录用户cookie
            #     7.1 获取cookie数据
            cookie_str = request.COOKIES.get('cart')
            #7.2判断cart数据是否存在
            if cookie_str is not None:
                cookie_cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_cart = {}
            if sku_id in cookie_cart:
                del cookie_cart[sku_id]
            response = Response(status=status.HTTP_204_NO_CONTENT)
            value = base64.b64encode(pickle.dumps(cookie_cart)).decode()
            response.set_cookie('cart',value)

            return response

