<script setup lang="ts">
import { ref } from 'vue'
import { Database, AlertCircle, CheckCircle2 } from 'lucide-vue-next'
import api from '../services/api'
import Sidebar from '../components/layout/Sidebar.vue'
import { useWindowSize } from '@vueuse/core'

const { width } = useWindowSize()
const isMobile = ref(width.value < 768)

const isSeeding = ref(false)
const seedSuccess = ref(false)
const seedError = ref('')

const triggerSeed = async () => {
  isSeeding.value = true
  seedSuccess.value = false
  seedError.value = ''
  
  try {
    await api.post('/seed')
    seedSuccess.value = true
  } catch (error: any) {
    seedError.value = error.response?.data?.detail || 'Failed to seed database'
  } finally {
    isSeeding.value = false
  }
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden font-sans">
    <Sidebar :isMobile="isMobile" />
    
    <main class="flex-1 overflow-y-auto pb-20 md:pb-0">
      <div class="p-6 md:p-10 max-w-4xl mx-auto space-y-6">
        
        <header class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900">Settings</h2>
          <p class="text-gray-500">Manage your account and developer tools.</p>
        </header>

        <!-- Developer Tools Section -->
        <section class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
          <div class="flex items-center space-x-3 mb-6">
            <div class="bg-emerald-100 p-2 rounded-lg">
              <Database class="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Developer Tools</h3>
              <p class="text-sm text-gray-500">Utilities for Phase 4 Testing</p>
            </div>
          </div>
          
          <div class="border-t border-gray-100 pt-6">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h4 class="font-medium text-gray-900">Generate Mock IoT Data</h4>
                <p class="text-sm text-gray-500 mt-1">
                  This will generate 12 default appliances and populate the PostgreSQL database with 30 days of realistic time-series energy and water readings (approx 35,000 rows).
                </p>
                <div v-if="seedError" class="mt-2 flex items-center text-sm text-red-600 bg-red-50 p-2 rounded">
                  <AlertCircle class="w-4 h-4 mr-2" /> {{ seedError }}
                </div>
                <div v-if="seedSuccess" class="mt-2 flex items-center text-sm text-emerald-600 bg-emerald-50 p-2 rounded">
                  <CheckCircle2 class="w-4 h-4 mr-2" /> Database successfully seeded! Go to Dashboard to see the real data.
                </div>
              </div>
              <button 
                @click="triggerSeed" 
                :disabled="isSeeding"
                class="whitespace-nowrap px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[140px]"
              >
                <span v-if="isSeeding" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                {{ isSeeding ? 'Seeding...' : 'Seed Database' }}
              </button>
            </div>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>
