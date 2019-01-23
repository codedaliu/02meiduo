from alipay import AliPay
from django.shortcuts import render

# Create your views here.
from rest_framework import status

from mall import settings
from orders.models import OrderInfo

'''
当用户点击支付的时候，需要让前端将订单ｉｄ传过来
该接口必须是登录用户

1.接受订单ｉｄ
2.根据订单ｉｄ查询订单对象
3.生成ａｌｉｐａｙ实力对象
4.调用支付接口生成order_string
5.拼接url
6.返回url

GET /order/(?<order_id>\d+)/payment/

'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
class PaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        #1.接受订单ｉｄ
        user = request.user
        #2.根据订单ｉｄ查询订单
        try:
            #为了查询的准确性，我们尽量多家几个条件
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        #3.生成alipay实力对象
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH)
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH)

        alipay = AliPay(
            appid = settings.ALIPAY_APPID,
            app_notify_url=None,#默认回调ｕｒｌ
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        #4.调用支付接口生成order_string
        subject = '测试订单'

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_app_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),  # total_amount是 decimal类型 要转换为 str
            subject=subject,
            return_url="http://www.meiduo.site:8080/pay_success.html",
            # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url)
        )
        #5.拼接url
        alipay_url = settings.ALIPAY_URL +'?'+ order_string
        #6.返回ｕｒｌ
        return Response({'alipay_url':alipay_url})
