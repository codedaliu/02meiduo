from django.conf.urls import url

from goods import views

urlpatterns=[
    url(r'^categories/(?P<category_id>\d+)/hotskus/$',views.HotSKUListAPIView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus/$',views.SKUListView.as_view()),
]


# 通过REST framework的router来定义路由
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls
