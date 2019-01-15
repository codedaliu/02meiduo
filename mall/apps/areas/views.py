from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ReadOnlyModelViewSet

from areas.models import Area
from areas.serializers import AreSerializer, SubAreaSerializer
from rest_framework_extensions.cache.mixins import RetrieveCacheResponseMixin

from rest_framework_extensions.cache.mixins import CacheResponseMixin

class AreaModelViewSet(CacheResponseMixin,ReadOnlyModelViewSet):

    def get_queryset(self):

        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()


    def get_serializer_class(self):
        #根据不同的业务逻辑返回不同的序列化器
        if self.action == 'list':
            return AreSerializer
        else:
            return SubAreaSerializer
