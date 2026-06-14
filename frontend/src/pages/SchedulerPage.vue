<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Sidebar from '../components/layout/Sidebar.vue'
import ScheduleTimeline from '../components/schedule/ScheduleTimeline.vue'
import ScheduleCard from '../components/schedule/ScheduleCard.vue'
import { Settings, RefreshCw, AlertTriangle, Lightbulb } from 'lucide-vue-next'
import api from '../services/api'
import { useWindowSize } from '@vueuse/core'

const { width } = useWindowSize()
const isMobile = ref(width.value < 768)

const isLoading = ref(true)
const errorMsg = ref('')
const gridForecast = ref([])
const recommendations = ref<any[]>([])
const summary = ref<any>(null)
const generatedAt = ref('')

const fetchSchedule = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const [forecastRes, recRes] = await Promise.all([
      api.get('/schedule/grid-forecast'),
      api.get('/schedule/recommendations')
    ])
    gridForecast.value = forecastRes.data
    recommendations.value = recRes.data.recommendations || []
    summary.value = recRes.data.daily_summary
    generatedAt.value = new Date(recRes.data.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (err: any) {
    console.error(err)
    errorMsg.value = "Could not generate schedule. Please try again."
  } finally {
    isLoading.value = false
  }
}

const acceptRec = async (id: str) => {
  try {
    await api.post(`/schedule/accept/${id}`)
    const rec = recommendations.value.find(r => r.id === id)
    if (rec) rec.status = 'accepted'
  } catch (err) {
    console.error(err)
  }
}

const dismissRec = async (id: str) => {
  try {
    await api.post(`/schedule/dismiss/${id}`)
    const rec = recommendations.value.find(r => r.id === id)
    if (rec) rec.status = 'dismissed'
  } catch (err) {
    console.error(err)
  }
}

const pendingRecs = computed(() => recommendations.value.filter(r => r.status === 'pending').sort((a,b) => a.priority_rank - b.priority_rank))
const actionedRecs = computed(() => recommendations.value.filter(r => r.status !== 'pending'))

onMounted(() => {
  fetchSchedule()
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden font-sans">
    <Sidebar :isMobile="isMobile" />
    
    <main class="flex-1 overflow-y-auto pb-20 md:pb-0">
      <div class="p-6 md:p-10 max-w-5xl mx-auto space-y-6">
        
        <header class="mb-8 flex justify-between items-end">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Smart Scheduler</h2>
            <p class="text-gray-500 text-sm mt-1">AI-powered scheduling to minimize cost and carbon emissions.</p>
          </div>
          <button @click="fetchSchedule" class="p-2 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors" title="Refresh">
            <RefreshCw class="w-5 h-5" :class="{'animate-spin text-emerald-600': isLoading}" />
          </button>
        </header>

        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
          <div class="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p class="text-gray-500 font-medium">Gemini is analyzing the energy grid...</p>
        </div>

        <div v-else-if="errorMsg" class="p-6 bg-red-50 rounded-2xl flex flex-col items-center text-center">
          <AlertTriangle class="w-10 h-10 text-red-500 mb-2" />
          <p class="text-red-800 font-bold mb-1">Analysis Failed</p>
          <p class="text-sm text-red-600">{{ errorMsg }}</p>
          <button @click="fetchSchedule" class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold">Try Again</button>
        </div>

        <div v-else-if="recommendations.length === 0" class="p-10 bg-white rounded-2xl border border-gray-100 text-center">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lightbulb class="w-8 h-8 text-gray-400" />
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">No Heavy Appliances Found</h3>
          <p class="text-gray-500 max-w-md mx-auto mb-6">We need to know about your heavy appliances (like a Washer or Dishwasher) to generate a schedule.</p>
          <router-link to="/settings" class="inline-flex items-center px-4 py-2 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-500 transition-colors">
            <Settings class="w-4 h-4 mr-2" /> Go to Settings
          </router-link>
        </div>

        <div v-else class="space-y-6">
          
          <!-- Summary Banner -->
          <div v-if="summary" class="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-2xl p-6 text-white shadow-lg">
            <div class="grid md:grid-cols-3 gap-6">
              <div>
                <p class="text-emerald-100 text-sm font-medium mb-1">Total Daily Savings</p>
                <p class="text-3xl font-black">${{ summary.total_estimated_cost.toFixed(2) }}</p>
              </div>
              <div>
                <p class="text-emerald-100 text-sm font-medium mb-1">Total Carbon Saved</p>
                <p class="text-3xl font-black">{{ Math.round(summary.total_carbon_saved) }}g <span class="text-sm font-normal opacity-80 text-emerald-200">CO₂</span></p>
              </div>
              <div class="bg-black/10 p-3 rounded-xl border border-white/10 flex items-start">
                <Lightbulb class="w-5 h-5 mr-2 text-emerald-300 flex-shrink-0 mt-0.5" />
                <p class="text-sm text-emerald-50 italic">"{{ summary.tip }}"</p>
              </div>
            </div>
            <p class="text-xs text-emerald-200/60 mt-4 text-right">Generated at {{ generatedAt }}</p>
          </div>

          <!-- Timeline Chart -->
          <ScheduleTimeline :gridForecast="gridForecast" :recommendations="recommendations" />

          <!-- Recommendations Lists -->
          <div class="grid md:grid-cols-2 gap-6">
            
            <!-- Pending -->
            <div>
              <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
                Action Required
                <span v-if="pendingRecs.length" class="ml-2 bg-amber-100 text-amber-700 py-0.5 px-2 rounded-full text-xs">{{ pendingRecs.length }}</span>
              </h3>
              
              <div v-if="pendingRecs.length === 0" class="p-6 bg-gray-50 border border-dashed border-gray-200 rounded-xl text-center text-gray-500 text-sm">
                All caught up!
              </div>
              
              <div class="space-y-4">
                <ScheduleCard v-for="rec in pendingRecs" :key="rec.id" :rec="rec" @accept="acceptRec" @dismiss="dismissRec" />
              </div>
            </div>

            <!-- Actioned -->
            <div>
              <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
                Your Schedule
                <span v-if="actionedRecs.length" class="ml-2 bg-gray-200 text-gray-700 py-0.5 px-2 rounded-full text-xs">{{ actionedRecs.length }}</span>
              </h3>
              
              <div v-if="actionedRecs.length === 0" class="p-6 bg-gray-50 border border-dashed border-gray-200 rounded-xl text-center text-gray-500 text-sm">
                Accept recommendations to build your daily schedule.
              </div>
              
              <div class="space-y-4">
                <ScheduleCard v-for="rec in actionedRecs" :key="rec.id" :rec="rec" />
              </div>
            </div>

          </div>
        </div>

      </div>
    </main>
  </div>
</template>
