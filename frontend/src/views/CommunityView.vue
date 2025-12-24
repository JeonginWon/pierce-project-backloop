<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const posts = ref([])
const topInvestors = ref([])
const showWriteModal = ref(false)
const currentSort = ref('latest') // 정렬 상태 추가

// 📝 글쓰기 데이터
const newPostTitle = ref('')
const newPostContent = ref('')
const newPostTicker = ref('')
const newPostImage = ref(null)

// 💬 상세 모달 상태
const selectedPost = ref(null)
const comments = ref([])
const newComment = ref('')

const API_BASE = '/api'

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const goToUserProfile = (userId) => {
  if (!userId) return;
  router.push(`/user/${userId}`);
}

// 📈 수익 상태에 따른 색상 결정
const getReturnColor = (val) => {
  const num = parseFloat(val)
  if (num > 0) return 'red'
  if (num < 0) return 'blue'
  return 'grey'
}

// 🔢 % 포맷 (기존 유지)
const formatReturnRate = (val) => {
  if (val === undefined || val === null) return '0'
  const num = parseFloat(val)
  return num > 0 ? `+${num}` : num.toString()
}

// 💰 금액 포맷 (천 단위 콤마)
const formatPrice = (val) => {
  if (!val) return '0'
  return Math.floor(val).toLocaleString()
}

// 🔄 정렬 기능 추가
const fetchData = async (sortType = currentSort.value) => {
  try {
    const feedRes = await fetch(`${API_BASE}/posts/feed/?sort=${sortType}`, {
      credentials: 'include'
    })
    if (feedRes.ok) {
      posts.value = await feedRes.json()
    } else if (feedRes.status === 401 && sortType === 'following') {
      alert('팔로잉 글 보기는 로그인이 필요합니다.')
      currentSort.value = 'latest'
      await fetchData('latest')
    }
    
    const rankRes = await fetch(`${API_BASE}/users/rank/top/`)
    if (rankRes.ok) topInvestors.value = await rankRes.json()
  } catch (e) { console.error(e) }
}

const changeSort = (sortType) => {
  if (sortType === 'following' && !authStore.isAuthenticated) {
    alert('팔로잉 글 보기는 로그인이 필요합니다.')
    return
  }
  currentSort.value = sortType
  fetchData(sortType)
}

const handleFileChange = (e) => {
  newPostImage.value = e.target.files[0]
}

const createPost = async () => {
  if (!authStore.isAuthenticated) return alert('로그인 필요')
  const formData = new FormData()
  formData.append('title', newPostTitle.value)
  formData.append('content', newPostContent.value)
  if (newPostTicker.value) formData.append('ticker', newPostTicker.value)
  if (newPostImage.value) formData.append('image', newPostImage.value)

  try {
    const res = await fetch(`${API_BASE}/posts/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
      body: formData
    })
    if (res.ok) {
      showWriteModal.value = false
      newPostTitle.value = ''; newPostContent.value = ''; newPostTicker.value = ''; newPostImage.value = null;
      await fetchData()
    }
  } catch (e) { console.error(e) }
}

const openDetail = async (post) => {
  selectedPost.value = post
  newComment.value = ''
  try {
    const res = await fetch(`${API_BASE}/posts/${post.id}/comments/`)
    if (res.ok) comments.value = await res.json()
  } catch (e) { console.error(e) }
}

const addComment = async () => {
  if (!authStore.isAuthenticated) return alert('로그인이 필요합니다.')
  if (!newComment.value.trim()) return
  try {
    const res = await fetch(`${API_BASE}/posts/${selectedPost.value.id}/comments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
      body: JSON.stringify({ content: newComment.value })
    })
    if (res.ok) {
      const created = await res.json()
      comments.value.push(created)
      newComment.value = ''
      selectedPost.value.comment_count++
    }
  } catch (e) { console.error(e) }
}

const toggleLike = async (post, event) => {
  if (event) event.stopPropagation()
  if (!authStore.isAuthenticated) return alert('로그인이 필요합니다.')
  try {
    const res = await fetch(`${API_BASE}/posts/${post.id}/like/`, { 
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
    })
    if (res.ok) {
      const data = await res.json()
      post.is_liked = data.liked
      post.like_count = data.like_count
    }
  } catch (e) { console.error(e) }
}

const getRankBadge = (index) => {
  if (index === 0) return '🥇'
  if (index === 1) return '🥈'
  if (index === 2) return '🥉'
  return ''
}

onMounted(fetchData)
</script>

<template>
  <div class="community-layout">
    <section class="feed-section">
      <div class="feed-header">
        <div class="header-text">
          <h2>투자의 발견</h2>
          <p class="subtitle">노하우를 공유하고 나만의 투자멘토를 찾아보세요.</p>
        </div>
        <button class="write-btn" @click="showWriteModal = true">글쓰기</button>
      </div>

      <!-- 🆕 정렬 탭 추가 -->
      <div class="sort-tabs">
        <button 
          :class="['sort-tab', { active: currentSort === 'latest' }]"
          @click="changeSort('latest')"
        >
          ⏰ 최신글
        </button>
        <button 
          :class="['sort-tab', { active: currentSort === 'popular' }]"
          @click="changeSort('popular')"
        >
          🔥 인기글
        </button>
        <button 
          :class="['sort-tab', { active: currentSort === 'following' }]"
          @click="changeSort('following')"
        >
          👥 팔로잉
        </button>
      </div>

      <!-- 결과 없을 때 메시지 -->
      <div v-if="posts.length === 0" class="empty-state">
        <p v-if="currentSort === 'following'">팔로우한 사용자의 글이 없습니다.</p>
        <p v-else>아직 게시글이 없습니다.</p>
      </div>

      <div v-for="post in posts" :key="post.id" class="post-card" @click="openDetail(post)">
        <div class="post-header">
          <div class="user-info-group clickable-wrapper" @click.stop="goToUserProfile(post.author.id)">
            <img :src="post.author.profile_image_url || '/default-profile.png'" class="avatar" />
            <div class="user-detail">
              <div class="name-row">
                <span class="nickname">{{ post.author.nickname }}</span>
                <span class="profit-badge" :class="getReturnColor(post.author.realized_profit)">
                  실현 {{ post.author.realized_profit > 0 ? '+' : '' }}{{ formatPrice(post.author.realized_profit) }}원
                </span>
              </div>
              <span class="post-date">{{ new Date(post.created_at).toLocaleDateString() }}</span>
            </div>
          </div>
          <span v-if="post.ticker" class="ticker-badge">{{ post.ticker }}</span>
        </div>
        
        <div class="post-body">
          <h3 class="post-title">{{ post.title }}</h3>
          <p class="post-excerpt">
            {{ post.content.length > 100 ? post.content.slice(0, 100) + '...' : post.content }}
            <span v-if="post.content.length > 100" class="more-link">더 보기</span>
          </p>
        </div>
        
        <div v-if="post.image_url" class="post-image-wrapper">
          <img :src="post.image_url" class="post-image" />
        </div>

        <div class="post-footer">
           <button class="action-btn" :class="{ active: post.is_liked }" @click.stop="toggleLike(post, $event)">
             {{ post.is_liked ? '❤️' : '🤍' }} {{ post.like_count }}
           </button>
           <span class="comment-icon">💬 {{ post.comment_count }}</span>
        </div>
      </div>
    </section>

    <aside class="sidebar">
      <div class="rank-card">
        <h3>🏆 수익 TOP 투자자</h3>
        <ul class="rank-list">
          <li v-for="(user, idx) in topInvestors" :key="user.id" class="rank-item">
            <div class="rank-user clickable-wrapper" @click="goToUserProfile(user.id)">
              <div class="rank-num">{{ idx + 1 }}</div>
              <img :src="user.profile_image_url || '/default-profile.png'" class="avatar-small" />
              <div class="rank-info">
                <span class="rank-name">{{ getRankBadge(idx) }} {{ user.nickname }}</span>
                <div class="rank-profit-group">
                  <span class="rank-rate" :class="getReturnColor(user.total_return_rate)">
                    {{ formatReturnRate(user.total_return_rate) }}%
                  </span>
                  <span class="rank-amount">{{ formatPrice(user.realized_profit) }}원</span>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </aside>
    
    <div v-if="showWriteModal" class="modal-overlay" @click.self="showWriteModal = false">
      <div class="modal-content write-modal">
        <h3>글 쓰기</h3>
        <div class="form-group">
           <input v-model="newPostTitle" placeholder="제목을 입력하세요" class="input-full title-input" />
        </div>
        <div class="form-group">
           <input v-model="newPostTicker" placeholder="관련 종목코드 (선택, 예: 005930)" class="input-full" />
        </div>
        <div class="form-group">
           <textarea v-model="newPostContent" placeholder="자유롭게 투자 이야기를 나누어보세요" class="textarea-full"></textarea>
        </div>
        <div class="form-group file-group">
           <input type="file" @change="handleFileChange" accept="image/*" class="file-input" />
        </div>
        <div class="modal-actions">
           <button @click="showWriteModal = false" class="cancel-btn">취소</button>
           <button @click="createPost" class="submit-btn">등록하기</button>
        </div>
      </div>
    </div>

    <!-- 📌 새로운 마이페이지 스타일 모달 -->
    <div v-if="selectedPost" class="modal-overlay-new" @click.self="selectedPost = null">
      <div class="modal-card-new">
        <div class="modal-inner">
          
          <!-- 헤더: 작성자 정보 + 닫기 버튼 -->
          <div class="modal-header-new">
            <div class="user-info-btn" @click.stop="goToUserProfile(selectedPost.author.id)">
              <img :src="selectedPost.author.profile_image_url || '/default-profile.png'" class="avatar-new" />
              <div class="user-text-new">
                <div class="nickname-new">{{ selectedPost.author.nickname }}</div>
                <div class="meta-row-new">
                  <span class="profit-badge-new" :class="getReturnColor(selectedPost.author.realized_profit)">
                    {{ formatPrice(selectedPost.author.realized_profit) }}원
                  </span>
                  <span class="date-new">{{ new Date(selectedPost.created_at).toLocaleString() }}</span>
                </div>
              </div>
            </div>
            <button class="close-btn-new" @click="selectedPost = null">✕</button>
          </div>

          <!-- 제목 -->
          <h2 class="post-title-new">
            <span v-if="selectedPost.ticker" class="ticker-badge-new">{{ selectedPost.ticker }}</span>
            {{ selectedPost.title }}
          </h2>

          <!-- 본문 -->
          <div class="post-body-new">
            <p class="post-content-new">{{ selectedPost.content }}</p>
            <img v-if="selectedPost.image_url" :src="selectedPost.image_url" class="post-image-new" />
          </div>

          <!-- 좋아요 버튼 -->
          <div class="actions-row-new">
            <button class="like-btn-new" :class="{ active: selectedPost.is_liked }" @click.stop="toggleLike(selectedPost)">
              <span class="heart-icon">{{ selectedPost.is_liked ? '❤️' : '🤍' }}</span>
              <span>좋아요 {{ selectedPost.like_count }}</span>
            </button>
          </div>

          <div class="divider-new"></div>

          <!-- 댓글 섹션 -->
          <div class="comments-section-new">
            <h3 class="comments-title-new">💬 댓글 {{ comments.length }}</h3>
            
            <div class="comment-list-new">
              <div v-for="cmt in comments" :key="cmt.id" class="comment-card-new">
                <div class="comment-author-new" @click.stop="goToUserProfile(cmt.author.id)">
                  {{ cmt.author.nickname }}
                </div>
                <div class="comment-text-new">{{ cmt.content }}</div>
              </div>
              <div v-if="comments.length === 0" class="no-comments-new">
                💭 첫 댓글을 남겨보세요!
              </div>
            </div>

            <div class="comment-input-wrapper-new">
              <input 
                v-model="newComment" 
                type="text" 
                placeholder="댓글을 남겨보세요..." 
                class="comment-input-new"
                @keyup.enter="addComment"
              />
              <button class="comment-submit-new" @click="addComment">등록</button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 🔴 레이아웃 및 공통 */
.community-layout { display: flex; gap: 40px; max-width: 1100px; margin: 0 auto; padding: 40px 20px; color: #f5f5f7; }
.feed-section { flex: 2; }
.sidebar { flex: 1; display: none; }
@media(min-width: 900px) { .sidebar { display: block; } }

/* 🟠 헤더 영역 */
.feed-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.header-text h2 { font-size: 28px; margin: 0 0 8px 0; font-weight: 800; }
.subtitle { color: #9ca3af; font-size: 15px; margin: 0; }
.write-btn { background: #2563eb; color: white; border: none; padding: 10px 24px; border-radius: 24px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.write-btn:hover { background: #1d4ed8; transform: scale(1.05); }

/* 🆕 정렬 탭 스타일 */
.sort-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid #222;
  padding-bottom: 0;
}

.sort-tab {
  background: none;
  border: none;
  color: #9ca3af;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
  position: relative;
  bottom: -1px;
}

.sort-tab:hover {
  color: #d1d5db;
}

.sort-tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

/* 빈 상태 메시지 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #6b7280;
  font-size: 15px;
}

/* 🟡 게시글 카드 (개선) */
.post-card { background: #14141409; padding: 24px; border-radius: 20px; margin-bottom: 24px; border: 1px solid #222; cursor: pointer; transition: 0.2s; }
.post-card:hover { border-color: #3b82f6; background: #1a1a1a07; }

.post-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.user-info-group { display: flex; align-items: center; gap: 12px; }
.avatar { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; background: #333333; }
.user-detail { display: flex; flex-direction: column; gap: 2px; }
.name-row { display: flex; align-items: center; gap: 8px; }
.nickname { font-weight: bold; font-size: 15px; }

/* 수익 뱃지 */
.profit-badge { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px; background: rgba(255, 255, 255, 0.05); }
.profit-badge.red { color: #ff4d4d; background: rgba(255, 77, 77, 0.1); }
.profit-badge.blue { color: #4d94ff; background: rgba(77, 148, 255, 0.1); }
.profit-badge.grey { color: #4a4a4aff; background: rgba(136, 136, 136, 0.1); }

.post-date { font-size: 12px; color: #6b7280; }
.ticker-badge { font-size: 11px; background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 4px 10px; border-radius: 8px; font-weight: 600; }

.post-title { font-size: 19px; font-weight: 700; margin: 0 0 10px 0; color: #f9fafb; }
.post-excerpt { font-size: 15px; color: #d1d5db; line-height: 1.6; margin-bottom: 12px; }
.more-link { color: #3b82f6; font-weight: 600; margin-left: 4px; }

.post-image-wrapper { margin: 16px 0; border-radius: 12px; overflow: hidden; border: 1px solid #222; }
.post-image { width: 100%; max-height: 450px; object-fit: cover; display: block; }

.post-footer { display: flex; align-items: center; gap: 20px; padding-top: 16px; border-top: 1px solid #222; color: #9ca3af; font-size: 14px; }
.action-btn { background: none; border: none; color: inherit; cursor: pointer; display: flex; align-items: center; gap: 6px; padding: 0; }
.action-btn.active { color: #ef4444; font-weight: bold; }

/* 🟢 사이드바 랭킹 */
.rank-card { background: #14141489; padding: 24px; border-radius: 20px; position: sticky; top: 100px; border: 1px solid #222; }
.rank-card h3 { margin: 0 0 20px 0; font-size: 18px; }
.rank-list { list-style: none; padding: 0; }
.rank-item { margin-bottom: 18px; }
.rank-user { display: flex; align-items: center; gap: 12px; }
.rank-num { width: 20px; font-weight: 800; color: #4b5563; font-style: italic; }
.avatar-small { width: 40px; height: 40px; border-radius: 50%; }
.rank-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.rank-profit-group { display: flex; align-items: center; gap: 8px; }
.rank-rate { font-size: 12px; font-weight: bold; }
.rank-amount { font-size: 12px; color: #9ca3af; }

/* 🔵 글쓰기 모달 (기존 유지) */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(8px); }
.modal-content { background: #1c1c1e; padding: 32px; border-radius: 24px; color: #f5f5f7; border: 1px solid #333; max-height: 90vh; overflow-y: auto; }
.write-modal { width: 90%; max-width: 600px; }

.input-full, .textarea-full { width: 100%; background: #000; border: 1px solid #333; color: white; padding: 14px; border-radius: 12px; margin-bottom: 12px; box-sizing: border-box; }
.textarea-full { height: 200px; resize: none; }

.submit-btn { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 12px; font-weight: bold; cursor: pointer; }
.cancel-btn { background: #333; color: white; border: none; padding: 12px 24px; border-radius: 12px; cursor: pointer; margin-right: 8px; }

.clickable-wrapper { cursor: pointer; transition: opacity 0.2s; }
.clickable-wrapper:hover { opacity: 0.7; }
.red { color: #ff4d4d !important; } 
.blue { color: #4d94ff !important; }
.grey { color: #888 !important; }

/* ========================================
   🎨 새로운 마이페이지 스타일 모달
   ======================================== */

.modal-overlay-new {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(12px);
  padding: 20px;
}

.modal-card-new {
  background: #1a1a1a;
  border: 1px solid #524f4f;
  border-radius: 20px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}

.modal-inner {
  padding: 32px;
}

/* 헤더 */
.modal-header-new {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.user-info-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 12px;
  transition: background 0.2s;
}

.user-info-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

.avatar-new {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.user-text-new {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nickname-new {
  font-weight: bold;
  font-size: 16px;
  color: white;
}

.meta-row-new {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.profit-badge-new {
  font-weight: bold;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 6px;
}

.profit-badge-new.red {
  color: #ff4d4d;
  background: rgba(255, 77, 77, 0.1);
}

.profit-badge-new.blue {
  color: #4d94ff;
  background: rgba(77, 148, 255, 0.1);
}

.profit-badge-new.grey {
  color: #888;
  background: rgba(136, 136, 136, 0.1);
}

.date-new {
  color: #9ca3af;
}

.close-btn-new {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: #9ca3af;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn-new:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* 제목 */
.post-title-new {
  font-size: 24px;
  font-weight: bold;
  color: white;
  margin: 0 0 20px 0;
  line-height: 1.4;
}

.ticker-badge-new {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-right: 8px;
  font-weight: 600;
}

/* 본문 */
.post-body-new {
  margin-bottom: 24px;
}

.post-content-new {
  font-size: 16px;
  line-height: 1.8;
  color: #e5e7eb;
  white-space: pre-wrap;
  margin: 0 0 20px 0;
}

.post-image-new {
  width: 100%;
  border-radius: 16px;
  margin-top: 20px;
  border: 1px solid #333;
}

/* 좋아요 버튼 */
.actions-row-new {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.like-btn-new {
  background: #1f2937;
  border: 1px solid #374151;
  color: #9ca3af;
  padding: 10px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.like-btn-new:hover {
  background: #374151;
}

.like-btn-new.active {
  color: #ef4444;
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.heart-icon {
  font-size: 18px;
}

/* 구분선 */
.divider-new {
  border: 0;
  border-top: 1px solid #333;
  margin: 24px 0;
}

/* 댓글 섹션 */
.comments-section-new {
  margin-top: 24px;
}

.comments-title-new {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0 0 16px 0;
}

.comment-list-new {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

/* 스크롤바 스타일 */
.comment-list-new::-webkit-scrollbar {
  width: 6px;
}

.comment-list-new::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.comment-list-new::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.comment-list-new::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.comment-card-new {
  background: #1f2937;
  padding: 14px;
  border-radius: 12px;
  margin-bottom: 10px;
  border: 1px solid #2d3748;
  transition: all 0.2s;
}

.comment-card-new:hover {
  background: #2d3748;
}

.comment-author-new {
  font-weight: bold;
  color: #60a5fa;
  font-size: 14px;
  margin-bottom: 6px;
  cursor: pointer;
  display: inline-block;
}

.comment-author-new:hover {
  opacity: 0.8;
}

.comment-text-new {
  color: #e5e7eb;
  line-height: 1.6;
  font-size: 14px;
}

.no-comments-new {
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
  font-size: 15px;
}

/* 댓글 입력 */
.comment-input-wrapper-new {
  display: flex;
  gap: 10px;
  background: #1f2937;
  padding: 8px;
  border-radius: 14px;
  border: 1px solid #333;
}

.comment-input-new {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  padding: 10px 14px;
  font-size: 15px;
  outline: none;
}

.comment-input-new::placeholder {
  color: #6b7280;
}

.comment-submit-new {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.comment-submit-new:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .modal-card-new {
    max-width: 100%;
    border-radius: 16px;
  }

  .modal-inner {
    padding: 20px;
  }

  .post-title-new {
    font-size: 20px;
  }

  .avatar-new {
    width: 40px;
    height: 40px;
  }
}
</style>