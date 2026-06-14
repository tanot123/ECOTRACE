<script setup lang="ts">
import { computed } from 'vue'
import { Play, Check, RefreshCw, AlertCircle } from 'lucide-vue-next'
import api from '../../services/api'

const props = defineProps<{
  challenge: any
  type: 'available' | 'active' | 'completed'
}>()

const emit = defineEmits(['refresh'])

// When active/completed, the data is a UserChallenge, so the template is nested
const template = computed(() => props.type === 'available' ? props.challenge : props.challenge.challenge)
const progress = computed(() => props.type === 'available' ? 0 : props.challenge.current_progress)
const target = computed(() => props.type === 'available' ? props.challenge.target_value : props.challenge.target_value)
const percent = computed(() => Math.min(100, Math.max(0, (progress.value / target.value) * 100)))

const getDifficultyColor = (diff: string) => {
  if (diff === 'easy') return 'bg-emerald-100 text-emerald-700'
  if (diff === 'medium') return 'bg-amber-100 text-amber-700'
  return 'bg-rose-100 text-rose-700'
}

const startChallenge = async () => {
  try {
    await api.post(`/challenges/${template.value.id}/start`)
    emit('refresh')
  } catch (err: any) {
    alert(err.response?.data?.detail || "Could not start challenge")
  }
}

const evaluateProgress = async () => {
  try {
    await api.post(`/challenges/${props.challenge.id}/evaluate`)
    emit('refresh')
  } catch (err) {
    console.error(err)
  }
}

const abandonChallenge = async () => {
  if (!confirm("Are you sure you want to forfeit this challenge?")) return
  try {
    await api.post(`/challenges/${props.challenge.id}/abandon`)
    emit('refresh')
  } catch (err: any) {
    alert(err.response?.data?.detail || "Could not abandon challenge")
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex flex-col transition-all hover:shadow-md">
    <div class="flex items-start justify-between mb-3">
      <div class="w-12 h-12 rounded-xl bg-gray-50 flex items-center justify-center text-2xl shrink-0">
        {{ template.icon }}
      </div>
      <div class="flex space-x-2">
        <span class="px-2 py-1 text-[10px] uppercase font-bold rounded-lg" :class="getDifficultyColor(template.difficulty)">
          {{ template.difficulty }}
        </span>
        <span class="px-2 py-1 text-[10px] uppercase font-bold rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-100">
          {{ template.points }} pts
        </span>
      </div>
    </div>
    
    <h4 class="font-bold text-gray-900 mb-1">{{ template.title }}</h4>
    <p class="text-xs text-gray-500 mb-4 flex-1">{{ template.description }}</p>

    <div v-if="type === 'active'">
      <div class="flex justify-between text-xs font-bold text-gray-700 mb-1">
        <span>Progress</span>
        <span>{{ progress }} / {{ target }} {{ template.target_unit }}</span>
      </div>
      <div class="h-2 w-full bg-gray-100 rounded-full overflow-hidden mb-4">
        <div class="h-full bg-emerald-500 transition-all" :style="`width: ${percent}%`"></div>
      </div>
      
      <div v-if="props.challenge.status === 'expired'" class="text-xs text-rose-500 font-bold flex items-center mb-4">
        <AlertCircle class="w-4 h-4 mr-1"/> Challenge Expired
      </div>

      <div class="flex space-x-2">
        <button v-if="props.challenge.status === 'active'" @click="evaluateProgress" class="flex-1 py-2 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-bold text-xs rounded-xl flex items-center justify-center transition-colors">
          <RefreshCw class="w-3 h-3 mr-1.5" /> Check Progress
        </button>
        <button v-if="props.challenge.status === 'active'" @click="abandonChallenge" class="py-2 px-3 bg-rose-50 text-rose-700 hover:bg-rose-100 font-bold text-xs rounded-xl flex items-center justify-center transition-colors" title="Forfeit Challenge">
          <AlertCircle class="w-4 h-4" />
        </button>
      </div>
    </div>

    <div v-if="type === 'available'">
      <div class="text-xs text-gray-500 mb-4 font-medium border-t border-gray-100 pt-3">
        Duration: {{ template.duration_days }} days
      </div>
      <button @click="startChallenge" class="w-full py-2 bg-gray-900 text-white hover:bg-emerald-600 font-bold text-xs rounded-xl flex items-center justify-center transition-colors">
        <Play class="w-3 h-3 mr-1.5" /> Start Challenge
      </button>
    </div>

    <div v-if="type === 'completed'" class="pt-3 border-t border-gray-100">
      <div class="w-full py-2 bg-emerald-50 text-emerald-700 font-bold text-xs rounded-xl flex items-center justify-center cursor-default">
        <Check class="w-4 h-4 mr-1.5" /> Completed
      </div>
    </div>

  </div>
</template>
