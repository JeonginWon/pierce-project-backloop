<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Devtools 데이터 구조인 selectedPost를 사용합니다.
const selectedPost = ref(null)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)

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

const postId = computed(() => route.params.id)

const fetchPostDetail = async () => {
  loading.value = true
  try {
    const postRes = await fetch(`${API_BASE}/posts/${postId.value}/`)
    if (postRes.ok) {
      selectedPost.value = await postRes.json()
    } else {
      alert('게시글을 찾을 수 없습니다.')
      router.push('/community')
      return
    }

    const commentsRes = await fetch(`${API_BASE}/posts/${postId.value}/comments/`)
    if (commentsRes.ok) {
      comments.value = await commentsRes.json()
    }
  } catch (e) {
    console.error('데이터 로드 실패:', e)
  } finally {
    loading.value = false
  }
}

// 👤 프로필 이동 함수
const goToUserProfile = (userId) => {
  console.log("유저 프로필 이동 시도. ID:", userId)
  if (!userId) {
    console.warn("userId가 없어 이동할 수 없습니다.")
    return
  }
  router.push(`/user/${userId}`)
}

const addComment = async () => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  if (!newComment.value.trim()) return

  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/comments/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
      body: JSON.stringify({ content: newComment.value })
    })

    if (res.ok) {
      const created = await res.json()
      comments.value.push(created)
      newComment.value = ''
      if (selectedPost.value) selectedPost.value.comment_count++
    }
  } catch (e) {
    console.error('댓글 등록 실패:', e)
  }
}

const toggleLike = async () => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/like/`, { 
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
    })
    if (res.ok) {
      const data = await res.json()
      selectedPost.value.is_liked = data.liked
      selectedPost.value.like_count = data.like_count
    }
  } catch (e) {
    console.error('좋아요 실패:', e)
  }
}

const goToPostDetail = (postId) => {
  // 게시글 상세 뷰의 경로가 /community/:id 형태라고 가정합니다.
  // 프로젝트의 실제 라우트 설정에 따라 이름을 사용하거나 경로를 수정하세요.
  router.push(`/community/${postId}`)
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchPostDetail()
})
</script>

<template>
  <div class="detail-page">
    <div v-if="loading" class="loading-area">
      <p>게시글을 불러오는 중...</p>
    </div>

    <div v-else-if="selectedPost" class="detail-container">
      <button @click="goBack" class="back-btn">← 목록으로</button>

      <div class="detail-card">
        <div class="detail-header">
          <button 
            type="button" 
            class="user-info-btn" 
            @click.stop="goToUserProfile(selectedPost.author.id)"
          >
            <img 
              :src="selectedPost.author.profile_image_url || '/default-profile.png'" 
              class="avatar" 
            />
            <div class="user-text">
              <div class="nickname">{{ selectedPost.author.nickname }}</div>
              <div class="meta-info">
                <span class="return-rate" :class="selectedPost.author.total_return_rate > 0 ? 'red' : 'blue'">
                  {{ selectedPost.author.total_return_rate > 0 ? '+' : '' }}{{ selectedPost.author.total_return_rate }}%
                </span>
                <span class="date">{{ new Date(selectedPost.created_at).toLocaleString() }}</span>
              </div>
            </div>
          </button>
        </div>

        <h1 class="detail-title">
          <span v-if="selectedPost.ticker" class="ticker-badge">{{ selectedPost.ticker }}</span>
          {{ selectedPost.title }}
        </h1>

        <div class="detail-body">
          <p>{{ selectedPost.content }}</p>
          <img v-if="selectedPost.image_url" :src="selectedPost.image_url" class="detail-image" />
        </div>

        <div class="detail-actions">
          <button class="action-btn" :class="{ active: selectedPost.is_liked }" @click.stop="toggleLike">
            {{ selectedPost.is_liked ? '❤️' : '🤍' }} 좋아요 {{ selectedPost.like_count }}
          </button>
        </div>

        <hr class="divider"/>

        <div class="comments-section">
          <h3>댓글 {{ comments.length }}</h3>
          <div class="comment-list">
            <div v-for="cmt in comments" :key="cmt.id" class="comment-item">
              <button 
                type="button" 
                class="cmt-author-btn" 
                @click.stop="goToUserProfile(cmt.author.id)"
              >
                {{ cmt.author.nickname }}
              </button>
              <span class="cmt-content">{{ cmt.content }}</span>
            </div>
            <div v-if="comments.length === 0" class="no-comments">첫 댓글을 남겨보세요!</div>
          </div>
          <div class="comment-input-area">
            <input v-model="newComment" type="text" placeholder="댓글을 남겨보세요..." @keyup.enter="addComment" />
            <button @click="addComment">등록</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ❗ 핵심 레이어 설정 */
.detail-page { max-width: 800px; margin: 0 auto; padding: 40px 20px; color: #f5f5f7; position: relative; z-index: 1; }
.detail-card { background: #141414; padding: 32px; border-radius: 16px; border: 1px solid #222; }

/* ❗ 유저 정보 버튼 스타일 (이미지/텍스트가 클릭을 방해하지 않게 처리) */
.user-info-btn {
  background: none;
  border: none;
  padding: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer !important;
  pointer-events: auto !important;
  text-align: left;
  border-radius: 12px;
  transition: background 0.2s;
  color: inherit;
  font-family: inherit;
}

.user-info-btn:hover { background: rgba(255, 255, 255, 0.08); }

/* ❗ 버튼 내부 요소들은 클릭 이벤트를 통과시켜야 함 */
.avatar, .user-text, .nickname, .meta-info, .return-rate, .date {
  pointer-events: none !important;
}

.avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.nickname { font-weight: bold; font-size: 16px; color: white; margin-bottom: 2px; }
.meta-info { display: flex; gap: 10px; font-size: 13px; color: #9ca3af; }

/* 댓글 작성자 버튼 스타일 */
.cmt-author-btn {
  background: none;
  border: none;
  padding: 0;
  margin-right: 10px;
  font-weight: bold;
  color: #60a5fa;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
  pointer-events: auto;
}
.cmt-author-btn:hover { text-decoration: underline; }

/* 기존 UI 스타일 유지 */
.loading-area { text-align: center; padding: 60px; color: #9ca3af; }
.back-btn { background: #374151; color: white; border: none; padding: 10px 20px; border-radius: 12px; cursor: pointer; margin-bottom: 24px; }
.red { color: #ff4d4d; }
.blue { color: #4d94ff; }
.detail-title { font-size: 26px; font-weight: bold; margin: 24px 0; line-height: 1.4; }
.ticker-badge { background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 4px 10px; border-radius: 6px; font-size: 14px; margin-right: 8px; }
.detail-body { line-height: 1.8; color: #e5e7eb; white-space: pre-wrap; margin-bottom: 30px; }
.detail-image { width: 100%; border-radius: 12px; margin-top: 20px; }
.action-btn { background: #1f2937; border: 1px solid #374151; color: #9ca3af; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.action-btn.active { color: #ef4444; border-color: #ef4444; }
.divider { border: 0; border-top: 1px solid #333; margin: 32px 0; }
.comment-item { background: #1f2937; padding: 12px; border-radius: 8px; margin-bottom: 8px; }
.comment-input-area { display: flex; gap: 8px; margin-top: 20px; }
.comment-input-area input { flex: 1; background: #1f2937; border: 1px solid #333; color: white; padding: 12px; border-radius: 8px; }
.comment-input-area button { background: #3b82f6; color: white; border: none; padding: 0 20px; border-radius: 8px; cursor: pointer; }
</style>