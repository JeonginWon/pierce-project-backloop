<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const selectedPost = ref(null)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)

// 수정 모드 관련
const isEditing = ref(false)
const editTitle = ref('')
const editContent = ref('')
const editTicker = ref('')

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

// 작성자 본인 확인
const isAuthor = computed(() => {
  return authStore.isAuthenticated && 
         selectedPost.value && 
         authStore.user?.id === selectedPost.value.author.id
})

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

const goToUserProfile = (userId) => {
  if (!userId) return
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

// 🆕 수정 모드 시작
const startEdit = () => {
  editTitle.value = selectedPost.value.title
  editContent.value = selectedPost.value.content
  editTicker.value = selectedPost.value.ticker || ''
  isEditing.value = true
}

// 🆕 수정 취소
const cancelEdit = () => {
  isEditing.value = false
}

// 🆕 수정 저장
const saveEdit = async () => {
  if (!editTitle.value.trim() || !editContent.value.trim()) {
    alert('제목과 내용을 입력해주세요.')
    return
  }

  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
      body: JSON.stringify({
        title: editTitle.value,
        content: editContent.value,
        ticker: editTicker.value
      })
    })

    if (res.ok) {
      const updated = await res.json()
      selectedPost.value.title = updated.title
      selectedPost.value.content = updated.content
      selectedPost.value.ticker = updated.ticker
      isEditing.value = false
      alert('수정되었습니다.')
    } else {
      alert('수정에 실패했습니다.')
    }
  } catch (e) {
    console.error('수정 실패:', e)
    alert('수정에 실패했습니다.')
  }
}

// 🆕 게시글 삭제
const deletePost = async () => {
  if (!confirm('정말 삭제하시겠습니까?')) return

  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
    })

    if (res.ok || res.status === 204) {
      alert('삭제되었습니다.')
      router.push('/community')
    } else {
      alert('삭제에 실패했습니다.')
    }
  } catch (e) {
    console.error('삭제 실패:', e)
    alert('삭제에 실패했습니다.')
  }
}

// 🆕 댓글 삭제
const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return

  try {
    const res = await fetch(`${API_BASE}/posts/comments/${commentId}/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
    })

    if (res.ok || res.status === 204) {
      comments.value = comments.value.filter(c => c.id !== commentId)
      if (selectedPost.value) selectedPost.value.comment_count--
    } else {
      alert('댓글 삭제에 실패했습니다.')
    }
  } catch (e) {
    console.error('댓글 삭제 실패:', e)
    alert('댓글 삭제에 실패했습니다.')
  }
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
        <!-- 헤더: 작성자 정보 + 수정/삭제 버튼 -->
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

          <!-- 🆕 작성자에게만 보이는 수정/삭제 버튼 -->
          <div v-if="isAuthor && !isEditing" class="post-actions">
            <button @click="startEdit" class="edit-btn">수정</button>
            <button @click="deletePost" class="delete-btn">삭제</button>
          </div>
        </div>

        <!-- 🆕 수정 모드 -->
        <div v-if="isEditing" class="edit-form">
          <input 
            v-model="editTicker" 
            placeholder="티커 (선택사항, 예: AAPL)" 
            class="edit-input" 
          />
          <input 
            v-model="editTitle" 
            placeholder="제목을 입력하세요" 
            class="edit-input" 
          />
          <textarea 
            v-model="editContent" 
            placeholder="내용을 입력하세요" 
            class="edit-textarea"
          ></textarea>
          <div class="edit-actions">
            <button @click="saveEdit" class="save-btn">저장</button>
            <button @click="cancelEdit" class="cancel-btn">취소</button>
          </div>
        </div>

        <!-- 일반 보기 모드 -->
        <div v-else>
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
        </div>

        <hr class="divider"/>

        <!-- 댓글 섹션 -->
        <div class="comments-section">
          <h3>댓글 {{ comments.length }}</h3>
          <div class="comment-list">
            <div v-for="cmt in comments" :key="cmt.id" class="comment-item">
              <div class="comment-header">
                <button 
                  type="button" 
                  class="cmt-author-btn" 
                  @click.stop="goToUserProfile(cmt.author.id)"
                >
                  {{ cmt.author.nickname }}
                </button>
                <!-- 🆕 댓글 작성자에게만 삭제 버튼 표시 -->
                <button 
                  v-if="authStore.user?.id === cmt.author.id"
                  @click="deleteComment(cmt.id)" 
                  class="cmt-delete-btn"
                >
                  삭제
                </button>
              </div>
              <span class="cmt-content">{{ cmt.content }}</span>
            </div>
            <div v-if="comments.length === 0" class="no-comments">첫 댓글을 남겨보세요!</div>
          </div>
          <div class="comment-input-area">
            <input 
              v-model="newComment" 
              type="text" 
              placeholder="댓글을 남겨보세요..." 
              @keyup.enter="addComment" 
            />
            <button @click="addComment">등록</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 기본 레이아웃 *//* =================================================================
   폰트 설정 (Bold)
   ================================================================= */
@font-face {
  font-family: 'HappinessSansBold';
  src: url('@/assets/fonts/Happiness-Sans-Bold.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

/* =================================================================
   기본 레이아웃 및 폰트 상속
   ================================================================= */
.detail-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  color: #f5f5f7;
  position: relative;
  z-index: 1;
}

.detail-card {
  background: #14141408;
  padding: 32px;
  border-radius: 20px;
  border: 1px solid #222;
}

/* 모든 버튼과 입력창에 기본 폰트 적용 */
button, input, textarea {
  font-family: inherit;
}

/* =================================================================
   공통 액션 버튼 (수정, 삭제, 저장, 등록 등)
   ================================================================= */
.edit-btn, .delete-btn, .save-btn, .cancel-btn, .comment-input-area button {
  font-family: 'HappinessSansBold', sans-serif;
  font-size: 16px;
  letter-spacing: -0.5px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.edit-btn:hover, .delete-btn:hover, .save-btn:hover, .cancel-btn:hover, .comment-input-area button:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

/* =================================================================
   헤더 및 상단 내비게이션
   ================================================================= */
.back-btn {
  background: #374151;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  cursor: pointer;
  margin-bottom: 24px;
  font-weight: bold;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.user-info-btn {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  text-align: left;
  border-radius: 12px;
  padding: 8px;
  transition: background 0.2s;
}

.user-info-btn:hover { background: rgba(255, 255, 255, 0.05); }

.avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.nickname { font-weight: bold; font-size: 16px; color: white; margin-bottom: 2px; }
.meta-info { display: flex; gap: 10px; font-size: 13px; color: #9ca3af; }
.red { color: #ff4d4d; }
.blue { color: #4d94ff; }

/* =================================================================
   게시글 액션 (작성자 전용)
   ================================================================= */
.post-actions {
  display: flex;
  gap: 12px;
}

.edit-btn {
  background: #2563eb;
  color: white;
  padding: 10px 20px;
  border-radius: 10px;
}

.delete-btn {
  background: #dc2626;
  color: white;
  padding: 10px 20px;
  border-radius: 10px;
}

/* =================================================================
   수정 모드 (Edit Form)
   ================================================================= */
.edit-form { margin: 20px 0; }

.edit-input, .edit-textarea {
  width: 100%;
  background: #1f2937;
  border: 1px solid #374151;
  color: white;
  padding: 14px;
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 16px;
}

.edit-textarea { min-height: 250px; resize: vertical; }

.edit-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.save-btn { background: #059669; color: white; padding: 12px 24px; border-radius: 10px; }
.cancel-btn { background: #4b5563; color: white; padding: 12px 24px; border-radius: 10px; }

/* =================================================================
   본문 영역
   ================================================================= */
.detail-title {
  font-family: 'HappinessSansBold', sans-serif;
  font-size: 28px;
  font-weight: bold;
  margin: 24px 0;
  line-height: 1.3;
}

.ticker-badge {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  margin-right: 10px;
  vertical-align: middle;
}

.detail-body {
  font-size: 17px;
  line-height: 1.8;
  color: #e5e7eb;
  white-space: pre-wrap;
  margin-bottom: 40px;
}

.detail-image { width: 100%; border-radius: 16px; margin-top: 20px; border: 1px solid #333; }

.action-btn {
  background: #1f2937;
  border: 1px solid #374151;
  color: #9ca3af;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: bold;
}

.action-btn.active { color: #ef4444; border-color: #ef4444; background: rgba(239, 68, 68, 0.05); }

.divider { border: 0; border-top: 1px solid #333; margin: 40px 0; }

/* =================================================================
   댓글 섹션
   ================================================================= */
.comments-section h3 {
  font-family: 'HappinessSansBold', sans-serif;
  font-size: 20px;
  margin-bottom: 20px;
}

.comment-item {
  background: #1f2937;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid #2d3748;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.cmt-author-btn {
  background: none;
  border: none;
  font-weight: bold;
  color: #60a5fa;
  cursor: pointer;
  font-size: 15px;
}

.cmt-delete-btn {
  font-family: 'HappinessSansBold', sans-serif;
  background: rgba(220, 38, 38, 0.1);
  color: #ef4444;
  border: 1px solid rgba(220, 38, 38, 0.2);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}

.cmt-delete-btn:hover { background: #dc2626; color: white; }

.cmt-content { color: #e5e7eb; line-height: 1.6; font-size: 15px; }

.comment-input-area {
  display: flex;
  gap: 10px;
  margin-top: 30px;
  background: #1f2937;
  padding: 8px;
  border-radius: 14px;
  border: 1px solid #333;
}

.comment-input-area input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  padding: 10px 14px;
  font-size: 16px;
}

.comment-input-area input:focus { outline: none; }

.comment-input-area button {
  background: #3b82f6;
  color: white;
  padding: 10px 24px;
  border-radius: 10px;
}

/* 유틸리티 */
.loading-area { text-align: center; padding: 100px; color: #9ca3af; font-size: 18px; }
.no-comments { text-align: center; color: #6b7280; padding: 30px; }
</style>