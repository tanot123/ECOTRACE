<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from '../components/layout/Sidebar.vue'
import ChallengeCard from '../components/challenges/ChallengeCard.vue'
import { Trophy, Star, Target } from 'lucide-vue-next'
import api from '../services/api'
import { useWindowSize } from '@vueuse/core'

const { width } = useWindowSize()
const isMobile = ref(width.value < 768)

const stats = ref<any>(null)
const available = ref([])
const active = ref([])
const completed = ref([])
const isLoading = ref(true)

const loadData = async () => {
  isLoading.value = true
  try {
    // Seed default challenges if missing
    await api.post('/challenges/seed')

    const [statsRes, availRes, actRes, compRes] = await Promise.all([
      api.get('/challenges/stats'),
      api.get('/challenges/available'),
      api.get('/challenges/active'),
      api.get('/challenges/completed')
    ])
    
    stats.value = statsRes.data
    available.value = availRes.data
    active.value = actRes.data
    completed.value = compRes.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden font-sans">
    <Sidebar :isMobile="isMobile" />
    
    <main class="flex-1 overflow-y-auto pb-20 md:pb-0">
      <div class="p-6 md:p-10 max-w-6xl mx-auto space-y-8">
        
        <header>
          <h2 class="text-2xl font-bold text-gray-900">Challenges & Gamification</h2>
          <p class="text-gray-500 text-sm mt-1">Complete eco-challenges to earn points and level up.</p>
        </header>

        <div v-if="isLoading" class="flex justify-center py-20">
          <div class="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>

        <template v-else>
          <!-- Stats Banner -->
          <div class="bg-gradient-to-br from-emerald-600 to-emerald-800 rounded-3xl p-6 md:p-8 text-white shadow-lg relative overflow-hidden">
            <div class="absolute -right-10 -top-10 text-9xl opacity-10">🏆</div>
            
            <div class="grid md:grid-cols-4 gap-6 relative z-10">
              <div class="md:col-span-2">
                <p class="text-emerald-100 text-sm font-bold uppercase tracking-wider mb-1">Your Eco-Level</p>
                <div class="flex items-center space-x-3 mb-2">
                  <span class="bg-white/20 px-3 py-1 rounded-full text-sm font-bold border border-white/20">Lvl {{ stats.current_level_num }}</span>
                  <h3 class="text-3xl font-black">{{ stats.current_level_title }}</h3>
                </div>
                <div class="w-full max-w-sm">
                  <div class="flex justify-between text-xs text-emerald-100 mb-1">
                    <span>{{ stats.total_points }} pts</span>
                    <span>Next Level: {{ stats.points_to_next_level }} more pts</span>
                  </div>
                  <div class="h-2 w-full bg-black/20 rounded-full overflow-hidden">
                    <div class="h-full bg-emerald-300" :style="`width: ${Math.min(100, (stats.total_points / (stats.total_points + stats.points_to_next_level)) * 100)}%`"></div>
                  </div>
                </div>
              </div>

              <div class="bg-black/10 rounded-2xl p-4 flex flex-col justify-center backdrop-blur-sm border border-white/10">
                <div class="flex items-center text-emerald-100 mb-2">
                  <Star class="w-4 h-4 mr-2" />
                  <span class="text-sm font-bold">Total Points</span>
                </div>
                <span class="text-3xl font-black">{{ stats.total_points }}</span>
              </div>
              
              <div class="bg-black/10 rounded-2xl p-4 flex flex-col justify-center backdrop-blur-sm border border-white/10">
                <div class="flex items-center text-emerald-100 mb-2">
                  <Target class="w-4 h-4 mr-2" />
                  <span class="text-sm font-bold">Challenges Met</span>
                </div>
                <span class="text-3xl font-black">{{ stats.challenges_completed }}</span>
              </div>
            </div>
          </div>

          <!-- Active Challenges -->
          <div>
            <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
              Active Challenges
              <span class="ml-2 text-xs font-bold text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">{{ stats.active_challenges_count }} / 3</span>
            </h3>
            
            <div v-if="active.length === 0" class="p-8 bg-white border border-dashed border-gray-300 rounded-2xl text-center text-gray-500 text-sm">
              You don't have any active challenges. Pick one below to get started!
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <ChallengeCard v-for="uc in active" :key="uc.id" :challenge="uc" type="active" @refresh="loadData" />
            </div>
          </div>

          <!-- Available Challenges -->
          <div v-if="available.length > 0">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Available To Start</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <ChallengeCard v-for="c in available" :key="c.id" :challenge="c" type="available" @refresh="loadData" />
            </div>
          </div>

          <!-- Completed Challenges -->
          <div v-if="completed.length > 0" class="opacity-75">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Completed</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <ChallengeCard v-for="uc in completed" :key="uc.id" :challenge="uc" type="completed" @refresh="loadData" />
            </div>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>
