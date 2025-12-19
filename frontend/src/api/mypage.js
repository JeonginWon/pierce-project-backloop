// src/api/mypage.js
import axios from './index'

export const mypageAPI = {
  // 내 정보 조회
  getMyInfo: () => axios.get('/users/me/'),
  
  // 포트폴리오 요약
  getPortfolioSummary: () => axios.get('/users/me/portfolio-summary/'),
  
  // 보유종목
  getHoldings: () => axios.get('/users/me/holdings/'),
  
  // 거래내역
  getTransactions: (limit = null) => {
    const params = limit ? { limit } : {}
    return axios.get('/users/me/transactions/', { params })
  },
  
  // 내 게시글
  getMyPosts: () => axios.get('/users/me/posts/'),
  
  // 좋아요한 게시글
  getLikedPosts: () => axios.get('/users/me/liked-posts/'),
  
  // 팔로워/팔로잉
  getFollowers: () => axios.get('/users/me/followers/'),
  getFollowing: () => axios.get('/users/me/following/'),
  
  // 관심종목
  getWatchlist: () => axios.get('/watchlist/'),
  toggleWatchlist: (ticker) => axios.post('/watchlist/toggle/', { ticker }),
  
  // 투자전략 메모
  getStrategyNotes: () => axios.get('/strategy-notes/'),
  createStrategyNote: (data) => axios.post('/strategy-notes/', data),
  updateStrategyNote: (id, data) => axios.put(`/strategy-notes/${id}/`, data),
  deleteStrategyNote: (id) => axios.delete(`/strategy-notes/${id}/`),
  
  // 회원정보 수정
  updateProfile: (userId, data) => axios.patch(`/users/${userId}/`, data),
}