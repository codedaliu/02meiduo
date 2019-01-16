from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

from contents.serializers import HotSKUListSerializer
from goods.models import SKU


class HomeAPIView(APIView):
    pass



'''
列表数据
热销数据：应该是到哪个分类去获取哪个分类的热销数据中

１．获取分裂ｉｄ
２．根据ｉｄ获取数据
３．将数据转化为字典
４返回相应

'''
from rest_framework.generics import ListAPIView
class HotSKUListAPIView(ListAPIView):
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]

    serializer_class = HotSKUListSerializer