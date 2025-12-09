from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Users
router.register(r'users', views.UserViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'follows', views.FollowViewSet)

# Stocks & Assets
router.register(r'stock-prices', views.StockDailyPriceViewSet)
router.register(r'holdings', views.StockHoldingViewSet)
router.register(r'transactions', views.TransactionHistoryViewSet)

# News (RAG)
router.register(r'historical-news', views.HistoricalNewsViewSet)
router.register(r'latest-news', views.LatestNewsViewSet)

# MyPage 
router.register(r'watchlist', views.WatchlistItemViewSet)
router.register(r'strategy-notes', views.StrategyNoteViewSet)


urlpatterns = [
    path('', include(router.urls)),
]