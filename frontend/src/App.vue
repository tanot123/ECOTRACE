<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()

onMounted(() => {
  // Check token on app load and validate
  authStore.initialize()
})
</script>

<template>
  <router-view></router-view>
</template>
