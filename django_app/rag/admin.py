from django.contrib import admin
from .models import (
    User, Post, Follow, 
    StockDailyPrice, StockHolding, TransactionHistory,
    HistoricalNews, LatestNews
)

# 1. 유저 & 소셜
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('following_user', 'follower_user')

# 2. 주식 데이터
@admin.register(StockDailyPrice)
class StockDailyPriceAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'trade_date', 'close', 'volume')
    list_filter = ('symbol',)
    search_fields = ('symbol',)

@admin.register(StockHolding)
class StockHoldingAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'quantity', 'average_buy_price')

@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'transaction_type', 'price', 'transaction_datetime')

# 3. 뉴스 (벡터 필드는 읽기 전용)
@admin.register(HistoricalNews)
class HistoricalNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'news_collection_date', 'impacted_ticker')
    readonly_fields = ('body_embedding_vector',) # 벡터 수정 방지

@admin.register(LatestNews)
class LatestNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'news_collection_date', 'views')
    readonly_fields = ('body_embedding_vector',)