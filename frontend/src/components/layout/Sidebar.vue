<script setup lang="ts">
import { Home, ScanLine, Calendar, Trophy, Settings, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const props = defineProps<{
  isMobile: boolean
}>()
</script>

<template>
  <nav :class="['bg-white border-r border-gray-200 flex flex-col', isMobile ? 'fixed bottom-0 w-full h-16 flex-row border-t border-r-0 z-50' : 'w-64 h-screen']">
    <div v-if="!isMobile" class="p-6">
      <h1 class="text-2xl font-bold text-emerald-600 tracking-tight flex items-center gap-2">
        EcoTrace <span class="text-xs bg-emerald-100 text-emerald-800 px-2 py-1 rounded-full">AI</span>
      </h1>
    </div>
    
    <div :class="[isMobile ? 'flex flex-row justify-around w-full' : 'flex flex-col flex-grow px-4 space-y-1']">
      <router-link to="/dashboard" class="flex items-center px-4 py-3 text-emerald-700 bg-emerald-50 rounded-lg" :class="isMobile ? 'flex-col justify-center px-2 py-1 bg-transparent text-xs' : ''">
        <Home class="w-5 h-5" :class="!isMobile && 'mr-3'" />
        <span :class="isMobile ? 'mt-1' : ''">Dashboard</span>
      </router-link>
      
      <a href="#" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors" :class="isMobile ? 'flex-col justify-center px-2 py-1 text-xs' : ''">
        <ScanLine class="w-5 h-5" :class="!isMobile && 'mr-3'" />
        <span :class="isMobile ? 'mt-1' : ''">Scanner</span>
      </a>
      
      <a href="#" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors" :class="isMobile ? 'flex-col justify-center px-2 py-1 text-xs' : ''">
        <Calendar class="w-5 h-5" :class="!isMobile && 'mr-3'" />
        <span :class="isMobile ? 'mt-1' : ''">Scheduler</span>
      </a>
      
      <a href="#" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors" :class="isMobile ? 'flex-col justify-center px-2 py-1 text-xs' : ''">
        <Trophy class="w-5 h-5" :class="!isMobile && 'mr-3'" />
        <span :class="isMobile ? 'mt-1' : ''">Challenges</span>
      </a>
      
      <router-link to="/settings" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors" :class="isMobile ? 'flex-col justify-center px-2 py-1 text-xs' : ''">
        <Settings class="w-5 h-5" :class="!isMobile && 'mr-3'" />
        <span :class="isMobile ? 'mt-1' : ''">Settings</span>
      </router-link>
    </div>

    <div v-if="!isMobile" class="p-4 border-t border-gray-200">
      <div class="bg-gray-50 rounded-xl p-4">
        <div class="flex items-center space-x-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 font-bold">
            {{ authStore.user?.display_name?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div>
            <p class="text-sm font-semibold text-gray-900">{{ authStore.user?.display_name }}</p>
            <p class="text-xs text-gray-500">Green Score: {{ authStore.user?.green_score || 0 }}</p>
          </div>
        </div>
        <button @click="authStore.logout" class="w-full flex items-center justify-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
          <LogOut class="w-4 h-4" />
          <span>Log Out</span>
        </button>
      </div>
    </div>
  </nav>
</template>
