from rest_framework.routers import DefaultRouter

from areas.views import AreaModelViewSet

urlpatterns=[

]
router = DefaultRouter()

#注册路由
router.register(r'infos',AreaModelViewSet,base_name='area')
#添加到
urlpatterns += router.urls


