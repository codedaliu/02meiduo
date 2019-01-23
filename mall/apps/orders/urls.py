from django.conf.urls import url

from orders import views

urlpatterns = [
    url(r'^places/$',views.PlaceOrderAPIView.as_view(),name = 'placeorder'),
    url(r'^$',views.OrederAPIView.as_view(),name='order')

]