<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <v-app>
    <v-main>
      <RouterView />
    </v-main>
  </v-app>
</template>

<style>
/* 👇 [필수] 앱 전체에 Noto Sans KR 폰트 강제 적용 */
:root, body, .v-application {
  font-family: 'Noto Sans KR', sans-serif !important;
  background-color: #121212; /* 배경색 유지 */
}

/* (선택사항) 스크롤바 디자인 */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #1e1e1e; }
::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #777; }
</style>