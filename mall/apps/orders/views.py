from _decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from goods.models import SKU
from orders.serializers import OrderPlaceSerializer, OrderSerializer


class PlaceOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        #1.我们获取用户信息
        user = request.user
        #2.从redis中获取数据
        redis_conn = get_redis_connection('cart')
        #hash
        redis_id_count = redis_conn.hgetall('cart_%s'%user.id)
        #　set
        selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)
        #获取的是二进制
        #需要的是选中的数据
        selected_cart = {}
        for sku_id in selected_ids:
            selected_cart[int(sku_id)] = int(redis_id_count[sku_id])
        #4.[sku_id,sku_id]
        ids = selected_cart.keys()
        #5.[SKU,SKU]
        skus = SKU.objects.filter(pk__in=ids)
        #6.返回响应

        freight = Decimal('10.00')

        serializer = OrderPlaceSerializer({
            'freight':freight,
            'skus':skus
        })

        return Response(serializer.data)

    '''
    提交订单
    1.接受前端的数据
    2.验证数据
    3.数据保存到数据库
    4.返回响应

    ＰＯＳＴ /orders/　
    '''
from rest_framework.generics import CreateAPIView
class OrederAPIView(CreateAPIView):

    def post(self,request):
        #接受前端的数据
        data = request.data
        #验证数据
        serializer = OrderSerializer

