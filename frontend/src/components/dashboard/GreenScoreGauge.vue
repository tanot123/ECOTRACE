<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUpRight, ArrowDownRight, ArrowRight } from 'lucide-vue-next'

const props = defineProps<{
  score: number
  trend: 'up' | 'down' | 'stable'
}>()

// Circle properties
const radius = 90
const circumference = 2 * Math.PI * radius
const strokeDashoffset = computed(() => {
  return circumference - (props.score / 100) * circumference
})

// Gradient color based on score
const gradientClass = computed(() => {
  if (props.score >= 80) return 'text-emerald-500'
  if (props.score >= 60) return 'text-green-400'
  if (props.score >= 40) return 'text-amber-400'
  return 'text-red-500'
})

</script>

<template>
  <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm flex flex-col items-center justify-center">
    <h3 class="text-base font-semibold text-gray-900 mb-2 self-start w-full">Green Score</h3>
    
    <div class="relative flex items-center justify-center mt-4">
      <!-- Background Circle -->
      <svg class="transform -rotate-90 w-48 h-48">
        <circle
          cx="96"
          cy="96"
          :r="radius"
          stroke="currentColor"
          stroke-width="12"
          fill="transparent"
          class="text-gray-100"
        />
        <!-- Progress Circle -->
        <circle
          cx="96"
          cy="96"
          :r="radius"
          stroke="currentColor"
          stroke-width="12"
          fill="transparent"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="strokeDashoffset"
          stroke-linecap="round"
          :class="['transition-all duration-1000 ease-out', gradientClass]"
        />
      </svg>
      
      <!-- Center Text -->
      <div class="absolute flex flex-col items-center">
        <span class="text-5xl font-black text-gray-900">{{ Math.round(score) }}</span>
        <div class="flex items-center mt-1 text-sm font-medium text-gray-500">
          <span v-if="trend === 'up'" class="flex items-center text-emerald-600">
            <ArrowUpRight class="w-4 h-4 mr-1" />
            +4.2
          </span>
          <span v-else-if="trend === 'down'" class="flex items-center text-red-500">
            <ArrowDownRight class="w-4 h-4 mr-1" />
            -2.1
          </span>
          <span v-else class="flex items-center text-gray-500">
            <ArrowRight class="w-4 h-4 mr-1" />
            0.0
          </span>
        </div>
      </div>
    </div>
    <p class="text-center text-sm text-gray-500 mt-6">
      Your sustainability score is improving! Keep up the great work.
    </p>
  </div>
</template>
