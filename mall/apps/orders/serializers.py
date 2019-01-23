from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods

class OrderSKUSerialzier(serializers.ModelSerializer):
    count = serializers.IntegerField(label='个数', read_only=True)

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price')


class OrderPlaceSerializer(serializers.Serializer):
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = OrderSKUSerialzier(many=True)

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self,validated_data):
        '''
        系统提供的create方法不能满足我们的需求，我们需要重写create

        当用户点击保存的按钮的时候，我们需要生成订单信息
        在生成订单列表信息


        1.生成订单信息
            1.1获取user信息
            1.2获取地址信息
            1.3获取支付方式
            1.4判断支付状态
            1.5订单ｉｄ
            1.6运费　价格和数量

        2.生成订单那商品列表信息
            2.1链接redis
            2.2 hash   set
            2.3选中的商品信息｛sku:count}
            2.4[sku_id,sku_id]
            2.5[SKU,SKU]
            2.6对列表进行遍历

                SKU 判断库存
                减少库存
                累加　计算总价格
                生成OrderGoods信息


        '''
        # 1.生成订单信息
        #     1.1获取user信息
        user = self.context['request'].user
        #     1.2获取地址信息
        address = validated_data['address']

        #     1.3获取支付方式
        pay_method = validated_data['pay_method']
        #     1.4判断支付状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            #货到付款
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        #     1.5订单ｉｄ
        #时间（年月日十分秒）　+6位用户的ｉｄ信息
        from django.utils import timezone
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%06d'.user.id

        #     1.6运费　价格和数量
        from decimal import Decimal
        freight = Decimal('10.00')
        total_count = 0
        total_amount = Decimal('0')
        #with 语法　实现　对部分代码实现事物的功能
        with transaction.atomic():
            #事物回滚点
            save_point = transaction.savepoint()
            #对象－－对象
            # 字段名－－值
            order = OrderInfo.objects.create(
                order_id = order_id,
                user = user,
                address = address,
                total_count = total_count,
                total_amount = total_amount,
                freight = freight,
                pay_method = pay_method,
                status=status
            )
            # 2.生成订单那商品列表信息
            #     2.1链接redis
            redis_coon = get_redis_connection('cart')
            #     2.2 hash   set
            redis_id_count = redis_coon.hgetall('cart_%s'%user.id)
            redis_selected_ids = redis_coon.smembers('cart_selected_%s'%user.id)

            #     2.3选中的商品信息｛sku:count}
            #组织一个选中商品的信息 selected_cart
            selected_cart = {}
            for sku_id in redis_selected_ids:
                selected_cart[int(sku_id)] = int(redis_id_count[sku_id])
            #     2.4[sku_id,sku_id]
            #     2.5[SKU,SKU]

            skus = SKU.objects.filter(pk__in=selected_cart.keys())


            #     2.6对列表进行遍历
            for sku in skus:
                #根据购买的书来嗯判断库存
                count = selected_cart[sku.id]
                if sku.stock < count:
                    #出现异常就应该回滚
                    #回滚到指定的保存点
                    transaction.savepoint_rollback(save_point)

                    raise serializers.ValidationError('库存不足')
                # 判断库存
                # 减少库存
                # 添加销量
                import time
                time.sleep(5)
                #使用乐观锁来实现
                old_stock = sku.stock-count
                old_sales = sku.sales + count

                new_stock = old_stock - count
                new_sales = old_sales + count

                rect = SKU.objects.filter(pk=sku.id,stock=old_stock).update(stock=new_stock,sales=new_sales)

                if rect ==0:
                    print('下单失败')

                    transaction.savepoint_rollback(save_point)

                    raise serializers.ValidationError('下单失败')

                #累加　计算总数量　和总价格
                order.total_count += count
                order.total_amount += (count*sku.price)

                OrderGoods.objects.create(
                    order=order,
                    sku = sku,
                    count=count,
                    price = sku.price
                )

                order.sace()

                transaction.savepoint_commit(save_point)
                #生成订单之后要注册　删除购物车

                return order
