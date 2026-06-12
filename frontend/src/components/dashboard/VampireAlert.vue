<script setup lang="ts">
import { Zap, Plug, CheckCircle2 } from 'lucide-vue-next'

const props = defineProps<{
  vampires: Array<{ name: string; standby_watts: number; yearly_cost: number }>
}>()
</script>

<template>
  <div class="bg-white rounded-2xl p-5 border border-amber-200 shadow-sm">
    <div class="flex items-center space-x-2 mb-4">
      <div class="bg-amber-100 p-2 rounded-lg">
        <Zap class="w-5 h-5 text-amber-600" />
      </div>
      <h3 class="text-base font-semibold text-gray-900">Energy Vampires Detected</h3>
    </div>
    
    <p class="text-sm text-gray-600 mb-4">
      We noticed these devices are consuming significant power while on standby.
    </p>

    <div class="space-y-3">
      <div v-for="(device, idx) in vampires" :key="idx" class="flex items-start justify-between bg-amber-50 rounded-xl p-3 border border-amber-100">
        <div class="flex items-start space-x-3">
          <Plug class="w-5 h-5 text-amber-500 mt-0.5" />
          <div>
            <p class="text-sm font-medium text-gray-900">{{ device.name }}</p>
            <p class="text-xs text-amber-700 mt-1">
              {{ device.standby_watts }}W standby • Est. ${{ device.yearly_cost }}/year
            </p>
          </div>
        </div>
        <button class="text-gray-400 hover:text-emerald-500 transition-colors" title="Mark as resolved">
          <CheckCircle2 class="w-5 h-5" />
        </button>
      </div>
    </div>
    
    <div v-if="vampires.length === 0" class="text-center py-6">
      <CheckCircle2 class="w-12 h-12 text-emerald-400 mx-auto mb-2" />
      <p class="text-sm font-medium text-gray-900">No vampires detected!</p>
      <p class="text-xs text-gray-500">Your appliances are running efficiently.</p>
    </div>
  </div>
</template>
