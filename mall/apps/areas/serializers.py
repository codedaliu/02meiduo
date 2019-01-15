from rest_framework import serializers

from areas.models import Area

#省信息序列化器
class AreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id','name']

# 市信息序列化器
class SubAreaSerializer(serializers.ModelSerializer):
    # area_set = AreSerializer(many=True)
    subs = AreSerializer(many=True)
    class Meta:
        model=Area
        # fields = ['area_set']
        fields = ['subs','id','name']


