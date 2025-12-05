from django.db import models
from pgvector.django import VectorField

# ==========================================
# 1. Users & Community (소셜, 피드)
# ==========================================

class User(models.Model):
    # 닉네임 중복 방지
    nickname = models.CharField(max_length=255, unique=True)
    # 해시된 비밀번호 저장
    password = models.CharField(max_length=255)
    profile_image_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nickname

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    # 게시글이 특정 종목에 대한 이야기일 경우 태그 (예: 005930)
    ticker = models.CharField(max_length=12, db_index=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.author.nickname}"

class Comment(models.Model):
    """피드 게시글에 달리는 댓글"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.nickname} on {self.post.id}"

class PostLike(models.Model):
    """게시글 좋아요 (중복 방지)"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 한 유저가 한 게시글에 좋아요는 한 번만 가능
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user.nickname} likes {self.post.id}"

class Follow(models.Model):
    following_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follower_user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['following_user', 'follower_user'], name='unique_follow')
        ]

# ==========================================
# 2. Stocks (주식 시세)
# ==========================================

class StockDailyPrice(models.Model):
    symbol = models.CharField(max_length=12, db_index=True) 
    trade_date = models.DateField()
    open = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    close = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    volume = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'trade_date'], name='unique_stock_price')
        ]

# ==========================================
# 3. Portfolio & Transactions (자산)
# ==========================================

class StockHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holdings')
    ticker = models.CharField(max_length=12, db_index=True)
    average_buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

class TransactionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    ticker = models.CharField(max_length=12, db_index=True)
    transaction_datetime = models.DateTimeField()
    transaction_type = models.CharField(max_length=10) # BUY / SELL
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

# ==========================================
# 4. News (RAG - Vector DB)
# ==========================================

class HistoricalNews(models.Model):
    news_collection_date = models.DateField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    url = models.URLField(max_length=2048, null=True, blank=True)
    
    # OpenAI 1536차원 벡터 (임베딩 실패 시 비워두기 허용)
    body_embedding_vector = VectorField(dimensions=1536, null=True, blank=True)
    
    # 뉴스에 관련된 종목들 (파이프라인 '|'으로 구분된 문자열 등)
    impacted_ticker = models.CharField(max_length=500, null=True, db_index=True)

class LatestNews(models.Model):
    news_collection_date = models.DateField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    url = models.URLField(max_length=2048, null=True, blank=True)
    
    # OpenAI 1536차원 벡터 (안전하게 null=True 추가)
    body_embedding_vector = VectorField(dimensions=1536, null=True, blank=True)
    
    views = models.IntegerField(default=0)