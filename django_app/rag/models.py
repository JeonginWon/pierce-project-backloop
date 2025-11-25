from django.db import models
from pgvector.django import VectorField

# ==========================================
# 1. Users & Social
# ==========================================

class User(models.Model):
    # ID는 Django가 자동으로 'id' 필드(Serial PK)를 생성합니다.
    nickname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    profile_image_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nickname

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    following_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follower_user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['following_user', 'follower_user'], name='unique_follow')
        ]

# ==========================================
# 2. Stocks (주식 데이터)
# ==========================================

class StockDailyPrice(models.Model):
    # Ticker(Symbol)는 중복될 수 있으므로(날짜별로), PK가 될 수 없습니다.
    # 대신 db_index=True를 걸어 검색 속도를 최적화합니다.
    symbol = models.CharField(max_length=12, db_index=True) 
    trade_date = models.DateField()
    open = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    close = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    volume = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # (종목, 날짜) 쌍은 유일해야 함
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'trade_date'], name='unique_stock_price')
        ]

# ==========================================
# 3. Portfolio & Transactions (자산 및 거래)
# ==========================================

class StockHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holdings')
    ticker = models.CharField(max_length=12, db_index=True) # StockDailyPrice.symbol과 논리적 연결
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
# 4. News (RAG용 벡터 데이터)
# ==========================================

class HistoricalNews(models.Model):
    news_collection_date = models.DateField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    body_embedding_vector = VectorField(dimensions=384) # MiniLM 모델 기준
    impacted_ticker = models.CharField(max_length=12, null=True, db_index=True)

class LatestNews(models.Model):
    news_collection_date = models.DateField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    body_embedding_vector = VectorField(dimensions=384)
    views = models.IntegerField(default=0)