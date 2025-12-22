<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const posts = ref([])
const topInvestors = ref([])
const showWriteModal = ref(false)

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

// 📈 색상 결정 (0일 때 회색 처리)
const getReturnColor = (val) => {
  const num = parseFloat(val)
  if (num > 0) return 'red'
  if (num < 0) return 'blue'
  return 'grey'
}

// 🔢 % 포맷
const formatReturnRate = (val) => {
  if (val === undefined || val === null) return '0'
  const num = parseFloat(val)
  return num > 0 ? `+${num}` : num.toString()
}

// 💰 원화 포맷 (추가됨!)
const formatPrice = (val) => {
  if (!val) return '0'
  return Math.floor(val).toLocaleString()
}

const fetchData = async () => {
  try {
    const feedRes = await fetch(`${API_BASE}/posts/feed/`)
    if (feedRes.ok) posts.value = await feedRes.json()
    
    const rankRes = await fetch(`${API_BASE}/users/rank/top/`)
    if (rankRes.ok) topInvestors.value = await rankRes.json()
  } catch (e) { console.error(e) }
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

      <div v-for="post in posts" :key="post.id" class="post-card" @click="openDetail(post)">
        <div class="post-meta">
          <div class="user-info clickable-wrapper" @click.stop="goToUserProfile(post.author.id)">
            <img :src="post.author.profile_image_url || '/default-profile.png'" class="avatar" />
            <div>
              <span class="nickname">{{ post.author.nickname }}</span>
              <span class="return-rate" :class="getReturnColor(post.author.total_return_rate)">
                실현 {{ formatReturnRate(post.author.total_return_rate) }}%
              </span>
            </div>
          </div>
          <span class="date">{{ new Date(post.created_at).toLocaleDateString() }}</span>
        </div>
        
        <h3>
           <span v-if="post.ticker" class="ticker-badge">{{ post.ticker }}</span>
           {{ post.title }}
        </h3>
        
        <div class="post-content">
          <p>
            {{ post.content.length > 100 ? post.content.slice(0, 100) + '...' : post.content }}
            <span v-if="post.content.length > 100" class="more-link">더 보기</span>
          </p>
        </div>
        
        <div v-if="post.image_url" class="post-image-wrapper">
          <img :src="post.image_url" class="post-image" />
        </div>

        <div class="post-actions">
           <button class="action-btn" :class="{ active: post.is_liked }" @click.stop="toggleLike(post, $event)">
             {{ post.is_liked ? '❤️' : '🤍' }} {{ post.like_count }}
           </button>
           <span class="comment-icon">💬 {{ post.comment_count }}</span>
        </div>
      </div>
    </section>

    <aside class="sidebar">
      <div class="rank-card">
        <h3>🏆 실현수익 상위 투자자</h3>
        <ul class="rank-list">
          <li v-for="(user, idx) in topInvestors" :key="user.id" class="rank-item">
            <span class="rank-num">{{ idx + 1 }}</span>
            <div class="rank-user clickable-wrapper" @click="goToUserProfile(user.id)">
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

    <div v-if="selectedPost" class="modal-overlay" @click.self="selectedPost = null">
      <div class="modal-content detail-modal">
        <div class="detail-header">
           <div class="user-info clickable-wrapper" @click.stop="goToUserProfile(selectedPost.author.id)">
            <img :src="selectedPost.author.profile_image_url || '/default-profile.png'" class="avatar" />
            <div>
              <div class="nickname">{{ selectedPost.author.nickname }}</div>
              <div class="date">{{ new Date(selectedPost.created_at).toLocaleString() }}</div>
            </div>
          </div>
        </div>
        <h2 class="detail-title">{{ selectedPost.title }}</h2>
        <div class="detail-body">
           <p>{{ selectedPost.content }}</p>
           <img v-if="selectedPost.image_url" :src="selectedPost.image_url" class="detail-image" />
        </div>
        <div class="detail-actions">
           <button class="action-btn" :class="{ active: selectedPost.is_liked }" @click="toggleLike(selectedPost)">
             {{ selectedPost.is_liked ? '❤️' : '🤍' }} 좋아요 {{ selectedPost.like_count }}
           </button>
        </div>
        <hr class="divider"/>
        <div class="comments-section">
          <h3>댓글 {{ comments.length }}</h3>
          <div class="comment-list">
            <div v-for="cmt in comments" :key="cmt.id" class="comment-item">
              <span class="cmt-author clickable-text" @click.stop="goToUserProfile(cmt.author.id)">
                {{ cmt.author.nickname }}
              </span>
              <span class="cmt-content">{{ cmt.content }}</span>
            </div>
          </div>
          <div class="comment-input-area">
            <input v-model="newComment" type="text" placeholder="댓글을 남겨보세요..." @keyup.enter="addComment"/>
            <button @click="addComment">등록</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 기존 스타일 유지 및 추가 */
.rank-profit-group { display: flex; align-items: center; gap: 8px; }
.rank-amount { font-size: 12px; color: #888; }

/* 🟢 수익률 색상 스타일 보강 */
.red { color: #ff4d4d !important; } 
.blue { color: #4d94ff !important; }
.grey { color: #888 !important; }

/* ... 나머지 기존 스타일 코드 ... */
.clickable-wrapper { position: relative; cursor: pointer; transition: opacity 0.2s; pointer-events: auto !important; }
.clickable-wrapper:hover { opacity: 0.8; }
.clickable-wrapper > * { pointer-events: none; }
.clickable-text { color: #60a5fa; font-weight: bold; cursor: pointer; }
.clickable-text:hover { text-decoration: underline; }
.community-layout { display: flex; gap: 40px; max-width: 1100px; margin: 0 auto; padding-top: 40px; color: #f5f5f7; }
.feed-section { flex: 2; }
.sidebar { flex: 1; display: none; }
@media(min-width: 900px) { .sidebar { display: block; } }
.feed-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; }
.header-text h2 { font-size: 28px; margin: 0 0 8px 0; }
.subtitle { color: #9ca3af; font-size: 15px; margin: 0; }
.write-btn { background: #2563eb; color: white; border: none; padding: 10px 24px; border-radius: 20px; font-weight: bold; cursor: pointer; transition: background 0.2s; white-space: nowrap; }
.write-btn:hover { background: #1d4ed8; }
.post-card { background: #141414; padding: 24px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #222; cursor: pointer; transition: transform 0.2s; }
.post-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
.user-info { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.avatar { width: 40px; height: 40px; border-radius: 50%; }
.nickname { font-weight: bold; font-size: 15px; }
.return-rate { font-size: 12px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.1); margin-left: 6px; border: 1px solid transparent; }
.red { border-color: rgba(255, 77, 77, 0.3); }
.blue { border-color: rgba(77, 148, 255, 0.3); }
.post-meta { display: flex; justify-content: space-between; color: #888; font-size: 13px; align-items: center; }
.post-content p { color: #d1d5db; line-height: 1.6; margin: 12px 0; }
.more-link { color: #60a5fa; font-weight: bold; margin-left: 8px; font-size: 14px; }
.ticker-badge { font-size: 12px; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 2px 6px; border-radius: 4px; vertical-align: middle; margin-right: 6px; }
.post-image-wrapper { margin-top: 12px; border-radius: 12px; overflow: hidden; }
.post-image { width: 100%; max-height: 400px; object-fit: cover; display: block; }
.post-actions { display: flex; gap: 16px; margin-top: 16px; color: #9ca3af; font-size: 14px; }
.action-btn { background: none; border: none; color: inherit; cursor: pointer; font-size: 14px; display: flex; align-items: center; gap: 4px; }
.action-btn.active { color: #ef4444; }
.rank-card { background: #1a1a1a; padding: 24px; border-radius: 16px; position: sticky; top: 100px; border: 1px solid #222; }
.rank-list { list-style: none; padding: 0; margin-top: 20px; }
.rank-item { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.rank-user { display: flex; align-items: center; gap: 12px; flex: 1; }
.avatar-small { width: 44px; height: 44px; border-radius: 50%; }
.rank-info { display: flex; flex-direction: column; font-size: 14px; }
.rank-name { font-weight: bold; }
.rank-rate { font-size: 13px; font-weight: bold; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(4px); }
.modal-content { background: #1f2937; padding: 32px; border-radius: 20px; color: #f5f5f7; box-shadow: 0 20px 50px rgba(0,0,0,0.5); display: flex; flex-direction: column; }
.write-modal { width: 90%; max-width: 800px; max-height: 90vh; }
.input-full { width: 100%; background: #111827; border: 1px solid #374151; color: white; padding: 14px; border-radius: 12px; box-sizing: border-box; font-size: 16px; }
.textarea-full { width: 100%; height: 300px; background: #111827; border: 1px solid #374151; color: white; padding: 14px; border-radius: 12px; resize: none; box-sizing: border-box; font-size: 16px; line-height: 1.6; }
.submit-btn { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px; }
.cancel-btn { background: #374151; color: white; border: none; padding: 12px 24px; border-radius: 12px; cursor: pointer; font-size: 16px; }
.detail-modal { width: 90%; max-width: 700px; max-height: 90vh; overflow-y: auto; }
.comment-item { background: #111827; padding: 12px; border-radius: 8px; margin-bottom: 10px; font-size: 14px; }
.comment-input-area { display: flex; gap: 10px; margin-top: 20px; }
.comment-input-area input { flex: 1; background: #111827; border: 1px solid #374151; color: white; padding: 12px; border-radius: 8px; }
.comment-input-area button { background: #3b82f6; color: white; border: none; padding: 0 20px; border-radius: 8px; cursor: pointer; }
.divider { border: 0; border-top: 1px solid #374151; margin: 20px 0; }
</style>