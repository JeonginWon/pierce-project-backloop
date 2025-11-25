from rest_framework import serializers
from .models import (
    User, Post, Follow, 
    StockDailyPrice, StockHolding, TransactionHistory,
    HistoricalNews, LatestNews
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

class StockDailyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockDailyPrice
        fields = '__all__'

class StockHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockHolding
        fields = '__all__'

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'

# RAG용 뉴스: 벡터값은 입력받지 않음 (Read Only)
class HistoricalNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalNews
        fields = '__all__'
        read_only_fields = ('body_embedding_vector',)

class LatestNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatestNews
        fields = '__all__'
        read_only_fields = ('body_embedding_vector',)