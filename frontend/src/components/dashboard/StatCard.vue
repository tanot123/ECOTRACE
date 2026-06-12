<script setup lang="ts">
import { ArrowUpRight, ArrowDownRight, ArrowRight } from 'lucide-vue-next'

const props = defineProps<{
  title: string
  value: string
  trend: 'up' | 'down' | 'stable'
  trendValue: string
  colorTheme: 'emerald' | 'blue' | 'amber'
}>()

const themeClasses = {
  emerald: {
    bg: 'bg-emerald-50',
    icon: 'text-emerald-500',
    text: 'text-emerald-700',
    trendUp: 'text-emerald-600',
    trendDown: 'text-red-500'
  },
  blue: {
    bg: 'bg-blue-50',
    icon: 'text-blue-500',
    text: 'text-blue-700',
    trendUp: 'text-blue-600',
    trendDown: 'text-gray-500'
  },
  amber: {
    bg: 'bg-amber-50',
    icon: 'text-amber-500',
    text: 'text-amber-700',
    trendUp: 'text-amber-600',
    trendDown: 'text-gray-500'
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-medium text-gray-500">{{ title }}</h3>
      <div :class="['p-2 rounded-lg', themeClasses[colorTheme].bg]">
        <slot name="icon"></slot>
      </div>
    </div>
    
    <div class="flex items-baseline space-x-2">
      <span class="text-3xl font-bold text-gray-900">{{ value }}</span>
    </div>
    
    <div class="mt-4 flex items-center text-sm">
      <span v-if="trend === 'up'" :class="['flex items-center font-medium', themeClasses[colorTheme].trendUp]">
        <ArrowUpRight class="w-4 h-4 mr-1" />
        {{ trendValue }}
      </span>
      <span v-else-if="trend === 'down'" :class="['flex items-center font-medium', themeClasses[colorTheme].trendDown]">
        <ArrowDownRight class="w-4 h-4 mr-1" />
        {{ trendValue }}
      </span>
      <span v-else class="flex items-center font-medium text-gray-500">
        <ArrowRight class="w-4 h-4 mr-1" />
        {{ trendValue }}
      </span>
      <span class="text-gray-500 ml-2">vs last week</span>
    </div>
  </div>
</template>
