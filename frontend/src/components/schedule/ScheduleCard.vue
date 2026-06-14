<script setup lang="ts">
import { DollarSign, Leaf, Zap, ChevronDown, ChevronUp, Check, X } from 'lucide-vue-next'
import { ref } from 'vue'

const props = defineProps<{
  rec: any
}>()

const emit = defineEmits(['accept', 'dismiss'])

const expanded = ref(false)
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border overflow-hidden transition-all duration-300" 
       :class="rec.status === 'accepted' ? 'border-emerald-300 ring-1 ring-emerald-300 bg-emerald-50/30' : rec.status === 'dismissed' ? 'opacity-50 border-gray-200 bg-gray-50' : 'border-gray-100 hover:border-emerald-200'">
    
    <div class="p-5">
      <div class="flex justify-between items-start mb-4">
        <div>
          <div class="flex items-center space-x-2 mb-1">
            <h4 class="font-bold text-gray-900 text-lg">{{ rec.appliance_name }}</h4>
            <span v-if="rec.status === 'accepted'" class="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] uppercase font-bold rounded-full">Accepted</span>
            <span v-if="rec.priority_rank === 1 && rec.status === 'pending'" class="px-2 py-0.5 bg-amber-100 text-amber-700 text-[10px] uppercase font-bold rounded-full">Top Pick</span>
          </div>
          <p class="text-sm font-medium text-emerald-600">Best time: {{ rec.recommended_start }} - {{ rec.recommended_end }}</p>
        </div>
      </div>

      <!-- Quick Metrics -->
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div class="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
          <DollarSign class="w-4 h-4 mx-auto text-emerald-500 mb-1" />
          <div class="text-xs text-gray-500">Save</div>
          <div class="font-bold text-gray-900">${{ rec.money_saved_usd.toFixed(2) }}</div>
        </div>
        <div class="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
          <Leaf class="w-4 h-4 mx-auto text-emerald-500 mb-1" />
          <div class="text-xs text-gray-500">Reduce</div>
          <div class="font-bold text-gray-900">{{ Math.round(rec.carbon_saved_grams) }}g</div>
        </div>
        <div class="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
          <Zap class="w-4 h-4 mx-auto text-emerald-500 mb-1" />
          <div class="text-xs text-gray-500">Renewable</div>
          <div class="font-bold text-gray-900">{{ Math.round(rec.renewable_percentage) }}%</div>
        </div>
      </div>

      <!-- Expandable Reasoning -->
      <div class="mb-4">
        <button @click="expanded = !expanded" class="flex items-center text-xs font-bold text-gray-500 hover:text-gray-700 w-full justify-between p-2 bg-gray-50 rounded-lg transition-colors">
          <span class="flex items-center"><Zap class="w-3 h-3 mr-1 text-emerald-500" /> AI Reasoning</span>
          <ChevronUp v-if="expanded" class="w-4 h-4" />
          <ChevronDown v-else class="w-4 h-4" />
        </button>
        <div v-if="expanded" class="mt-2 p-3 bg-blue-50 text-blue-900 text-sm rounded-lg border border-blue-100">
          "{{ rec.reasoning }}"
        </div>
      </div>

      <!-- Actions -->
      <div v-if="rec.status === 'pending'" class="flex space-x-3 pt-2 border-t border-gray-100">
        <button @click="emit('dismiss', rec.id)" class="flex-1 py-2 text-sm font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors flex justify-center items-center">
          <X class="w-4 h-4 mr-1.5" /> Skip
        </button>
        <button @click="emit('accept', rec.id)" class="flex-1 py-2 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-sm shadow-emerald-200 transition-colors flex justify-center items-center">
          <Check class="w-4 h-4 mr-1.5" /> Accept Time
        </button>
      </div>
    </div>
  </div>
</template>
