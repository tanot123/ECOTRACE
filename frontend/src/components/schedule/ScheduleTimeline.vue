<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  gridForecast: any[]
  recommendations: any[]
}>()

// Calculate max renewable for the Y axis of the area chart
const maxRenewable = computed(() => {
  if (!props.gridForecast || props.gridForecast.length === 0) return 100
  return Math.max(...props.gridForecast.map(f => f.total_renewable_percentage))
})

const getTierColor = (tier: string) => {
  switch (tier) {
    case 'off_peak': return 'bg-emerald-400'
    case 'mid_peak': return 'bg-amber-400'
    case 'on_peak': return 'bg-rose-500'
    default: return 'bg-gray-300'
  }
}

const formatHour = (hour24: number) => {
  if (hour24 === 0) return '12A'
  if (hour24 === 12) return '12P'
  return hour24 > 12 ? `${hour24 - 12}P` : `${hour24}A`
}

// Convert HH:MM to an offset percentage
const timeToPercent = (timeStr: string) => {
  if (!timeStr) return 0
  const [h, m] = timeStr.split(':').map(Number)
  // assuming the timeline starts at hour 0, but our forecast might start at the current hour.
  // For simplicity, let's map 0-24 hours to 0-100% width
  return ((h + m / 60) / 24) * 100
}

</script>

<template>
  <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-8 overflow-x-auto">
    <div class="min-w-[700px]">
      <div class="flex justify-between items-end mb-4">
        <h3 class="font-bold text-gray-900">24-Hour Grid Forecast & Schedule</h3>
        <div class="flex space-x-4 text-xs font-medium text-gray-500">
          <div class="flex items-center"><div class="w-3 h-3 rounded-full bg-emerald-400 mr-1.5"></div> Off-Peak</div>
          <div class="flex items-center"><div class="w-3 h-3 rounded-full bg-amber-400 mr-1.5"></div> Mid-Peak</div>
          <div class="flex items-center"><div class="w-3 h-3 rounded-full bg-rose-500 mr-1.5"></div> On-Peak</div>
        </div>
      </div>

      <!-- Timeline Wrapper -->
      <div class="relative h-48 border-b border-gray-200 mt-8">
        
        <!-- Y-Axis labels (Renewable %) -->
        <div class="absolute left-0 top-0 bottom-0 w-8 flex flex-col justify-between text-[10px] text-emerald-600 font-bold opacity-50 z-10 pointer-events-none">
          <span>{{ Math.round(maxRenewable) }}%</span>
          <span>0%</span>
        </div>

        <!-- The main timeline grid -->
        <div class="absolute left-8 right-0 top-0 bottom-0 flex">
          
          <!-- Pricing Band background -->
          <div class="absolute bottom-0 left-0 right-0 h-2 flex">
            <div v-for="(f, i) in gridForecast" :key="`band-${i}`" class="flex-1 h-full opacity-80" :class="getTierColor(f.pricing_tier)"></div>
          </div>

          <!-- Renewable Overlay (Bars to simulate area) -->
          <div class="absolute bottom-2 left-0 right-0 top-0 flex items-end opacity-20 pointer-events-none">
            <div v-for="(f, i) in gridForecast" :key="`solar-${i}`" class="flex-1 border-r border-emerald-100 border-opacity-50" :style="`height: ${(f.total_renewable_percentage / maxRenewable) * 100}%; background: linear-gradient(180deg, #10b981 0%, transparent 100%);`"></div>
          </div>

          <!-- Recommendations Overlay -->
          <div class="absolute top-4 bottom-8 left-0 right-0">
            <div v-for="(rec, i) in recommendations" :key="rec.id" 
                 class="absolute h-10 rounded-lg shadow-sm border border-emerald-500 bg-emerald-50 flex items-center px-2 cursor-pointer hover:bg-emerald-100 transition-colors z-20 group"
                 :style="`left: ${timeToPercent(rec.recommended_start)}%; width: ${timeToPercent(rec.recommended_end) - timeToPercent(rec.recommended_start)}%; top: ${i * 44}px;`">
              <span class="text-xs font-bold text-emerald-800 truncate">{{ rec.appliance_name }}</span>
              <!-- Hover Tooltip -->
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 bg-gray-900 text-white text-xs p-2 rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-30">
                <p class="font-bold mb-1">{{ rec.appliance_name }}</p>
                <p>{{ rec.recommended_start }} - {{ rec.recommended_end }}</p>
                <p class="text-emerald-400 mt-1">Save ${{ rec.money_saved_usd.toFixed(2) }}</p>
              </div>
            </div>
          </div>

          <!-- X-Axis Labels (Hours) -->
          <div class="absolute top-full mt-2 left-0 right-0 flex justify-between text-[10px] font-bold text-gray-400">
             <div v-for="(f, i) in gridForecast" :key="`hour-${i}`" class="flex-1 text-center border-l border-gray-200 h-2 -mt-2 pt-3">
               <span v-if="i % 2 === 0">{{ formatHour(f.hour) }}</span>
             </div>
          </div>
          
        </div>
      </div>
      <div class="mt-8 text-center text-xs text-emerald-600 font-medium">
        <span class="opacity-70">Green background wave indicates renewable energy availability</span>
      </div>
    </div>
  </div>
</template>
