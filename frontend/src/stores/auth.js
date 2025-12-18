import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const error = ref(null)
  const router = useRouter()
  
  const API_BASE = '/api'

  // 🍪 CSRF 토큰 가져오는 헬퍼 함수 (POST 요청 시 필수)
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

  // 1. 로그인 (username, password 사용)
  const login = async (username, password) => {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${API_BASE}/users/login/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'), // 🛡️ CSRF 헤더 추가
        },
        // 👇 nickname 대신 username 사용 (Django 기본값)
        body: JSON.stringify({ username, password }),
        credentials: 'include' 
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || data.message || '로그인에 실패했습니다.')
      }

      await fetchUser()
      return true
    } catch (err) {
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }

  // 2. 회원가입 (모든 필드 전송하도록 수정)
  // 👇 인자를 객체(payload)로 받음
  const register = async (payload) => {
    loading.value = true
    error.value = null
    try {
      // payload에서 필요한 정보 추출
      const { username, password, email, nickname } = payload
      
      // 랜덤 프로필 이미지 생성 (username 기준)
      const profile_image_url = `https://api.dicebear.com/7.x/adventurer/svg?seed=${username}`

      const res = await fetch(`${API_BASE}/users/register/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'), // 🛡️ CSRF 헤더 추가
        },
        // 👇 모든 필드를 백엔드로 전송
        body: JSON.stringify({ 
          username, 
          password,
          email,
          nickname,
          profile_image_url 
        }),
      })

      if (!res.ok) {
        // 에러 응답 파싱 (Django는 보통 객체 형태로 에러를 줌)
        const data = await res.json().catch(() => ({}))
        // 에러 메시지가 배열이나 객체일 경우를 대비해 문자열로 변환
        const errorMsg = typeof data === 'object' ? JSON.stringify(data) : data
        throw new Error(errorMsg || '회원가입에 실패했습니다.')
      }
      
      return true
    } catch (err) {
      // 보기 좋게 에러 메시지 정제
      let msg = err.message
      if (msg.includes('username')) msg = "이미 존재하는 아이디입니다."
      else if (msg.includes('email')) msg = "이미 사용 중인 이메일입니다."
      
      error.value = msg
      return false
    } finally {
      loading.value = false
    }
  }

  // 3. 내 정보 가져오기
  const fetchUser = async () => {
    try {
      const res = await fetch(`${API_BASE}/users/me/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      })
      
      if (res.ok) {
        const userData = await res.json()
        user.value = userData
        isAuthenticated.value = true
      } else {
        user.value = null
        isAuthenticated.value = false
      }
    } catch (err) {
      console.error(err)
      user.value = null
      isAuthenticated.value = false
    }
  }

  // 4. 로그아웃
  const logout = async () => {
    try {
      await fetch(`${API_BASE}/users/logout/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'include'
      })
    } catch (err) {
      console.error(err)
    } finally {
      user.value = null
      isAuthenticated.value = false
      window.location.href = '/' // 깔끔하게 새로고침하며 이동
    }
  }

  return { 
    user, 
    isAuthenticated, 
    loading, 
    error, 
    login, 
    register, 
    fetchUser, 
    logout, 
  }
})