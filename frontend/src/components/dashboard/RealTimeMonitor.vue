<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Activity } from 'lucide-vue-next'
import api from '../../services/api'

const totalWatts = ref(0)
const activeCount = ref(0)
const lastUpdated = ref(new Date())

let pollInterval: ReturnType<typeof setInterval>

const fetchRealtimeData = async () => {
  try {
    const response = await api.get('/energy/realtime')
    totalWatts.value = response.data.total_watts_now
    activeCount.value = response.data.active_appliances
    lastUpdated.value = new Date()
  } catch (err) {
    console.error('Failed to fetch realtime data', err)
  }
}

onMounted(() => {
  fetchRealtimeData()
  pollInterval = setInterval(fetchRealtimeData, 5000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<template>
  <div class="bg-gray-900 rounded-2xl p-5 shadow-sm text-white relative overflow-hidden">
    <!-- Pulse Effect Background -->
    <div class="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-emerald-500 rounded-full opacity-10 animate-pulse"></div>
    
    <div class="flex items-center justify-between mb-4 relative z-10">
      <h3 class="text-sm font-medium text-gray-300">Live Power Draw</h3>
      <div class="flex items-center space-x-2">
        <span class="relative flex h-3 w-3">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </span>
        <span class="text-xs text-gray-400">Live</span>
      </div>
    </div>
    
    <div class="flex items-baseline space-x-2 relative z-10">
      <span class="text-4xl font-black text-white">{{ Math.round(totalWatts) }}</span>
      <span class="text-emerald-400 font-semibold">Watts</span>
    </div>
    
    <div class="mt-4 flex items-center justify-between text-sm text-gray-400 relative z-10">
      <div class="flex items-center">
        <Activity class="w-4 h-4 mr-1 text-gray-500" />
        {{ activeCount }} appliances active
      </div>
      <div class="text-xs">
        Updated {{ lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) }}
      </div>
    </div>
  </div>
</template>
