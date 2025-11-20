from rest_framework import serializers
from .models import VectorTest, Member

class VectorTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorTest
        fields = '__all__'
        # 👇 이 줄을 추가하면 됩니다!
        # "embedding 필드는 입력받지 말고, 보여주기만 해라" 라는 뜻입니다.
        read_only_fields = ['embedding'] 

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'