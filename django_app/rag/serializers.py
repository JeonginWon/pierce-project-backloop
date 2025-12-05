from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    User, Post, Follow,
    StockDailyPrice, StockHolding, TransactionHistory,
    HistoricalNews, LatestNews,
    Comment, PostLike,
)

# ==========================================
# 1. User (회원가입, 로그인, 조회)
# ==========================================

# (1) 읽기 전용: 유저 정보를 보여줄 때 사용 (비밀번호 제외)
class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nickname", "profile_image_url")

# (2) 쓰기 전용: 회원가입/수정 시 사용 (비밀번호 해싱 처리)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nickname", "password", "profile_image_url")
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def create(self, validated_data):
        # 비밀번호를 평문으로 저장하지 않고 암호화(Hash)해서 저장
        raw_password = validated_data.get("password")
        validated_data["password"] = make_password(raw_password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 비밀번호 변경 시에만 암호화 수행
        password = validated_data.get("password", None)
        if password:
            validated_data["password"] = make_password(password)
        return super().update(instance, validated_data)

# (3) 로그인 요청 검증용 (DB 저장 안 함)
class UserLoginSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    password = serializers.CharField(write_only=True)


# ==========================================
# 2. Feed & Community (게시글, 댓글, 팔로우)
# ==========================================

class CommentSerializer(serializers.ModelSerializer):
    # 작성자 정보는 읽기 전용으로 상세하게 보여줌
    author = UserReadSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "content", "created_at")
        read_only_fields = ("id", "post", "author", "created_at")


class PostWriteSerializer(serializers.ModelSerializer):
    """글 작성/수정용 시리얼라이저"""
    class Meta:
        model = Post
        fields = ("id", "title", "content", "ticker", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class PostReadSerializer(serializers.ModelSerializer):
    """글 조회용 시리얼라이저 (작성자 정보, 좋아요 여부 포함)"""
    author = UserReadSerializer(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id", "title", "content", "author", "ticker",
            "created_at", "updated_at",
            "comment_count", "like_count", "is_liked",
        )

    def get_is_liked(self, obj):
        """현재 로그인한 유저가 좋아요를 눌렀는지 확인"""
        request = self.context.get("request")
        if not request:
            return False
        # 세션에서 user_id 가져오기
        user_id = request.session.get("user_id")
        if not user_id:
            return False
        return obj.likes.filter(user_id=user_id).exists()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


# ==========================================
# 3. Stocks & Assets (주식, 자산)
# ==========================================

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


# ==========================================
# 4. News & RAG (뉴스, 벡터)
# ==========================================

class HistoricalNewsSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = HistoricalNews
        fields = '__all__'
        # 임베딩 벡터는 서버가 자동 생성하므로 사용자가 입력하지 못하게 함
        read_only_fields = ('body_embedding_vector',)

class LatestNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatestNews
        fields = '__all__'
        read_only_fields = ('body_embedding_vector',)