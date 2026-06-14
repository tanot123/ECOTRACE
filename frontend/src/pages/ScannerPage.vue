<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from '../components/layout/Sidebar.vue'
import ScannerCapture from '../components/scanner/ScannerCapture.vue'
import ScanResultCard from '../components/scanner/ScanResultCard.vue'
import { Receipt, Box, Barcode, AlertTriangle } from 'lucide-vue-next'
import api from '../services/api'
import { useWindowSize } from '@vueuse/core'

const { width } = useWindowSize()
const isMobile = ref(width.value < 768)

const isProcessing = ref(false)
const scanType = ref('receipt')
const scanResult = ref<any>(null)
const errorMsg = ref('')

const handleCapture = async (file: File) => {
  isProcessing.value = true
  errorMsg.value = ''
  scanResult.value = null
  
  const formData = new FormData()
  formData.append('image', file)
  formData.append('scan_type', scanType.value)
  
  try {
    const response = await api.post('/scan/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.status === 'error') {
      errorMsg.value = response.data.analysis.message || 'Gemini could not analyze this image.'
    } else {
      scanResult.value = response.data.analysis
    }
  } catch (err: any) {
    console.error(err)
    errorMsg.value = err.response?.data?.detail || 'An error occurred during analysis.'
  } finally {
    isProcessing.value = false
  }
}

const reset = () => {
  scanResult.value = null
  errorMsg.value = ''
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden font-sans">
    <Sidebar :isMobile="isMobile" />
    
    <main class="flex-1 overflow-y-auto pb-20 md:pb-0">
      <div class="p-6 md:p-10 max-w-4xl mx-auto space-y-6">
        
        <header class="mb-6 flex justify-between items-center">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Gemini AI Scanner</h2>
            <p class="text-gray-500 text-sm mt-1">Scan receipts or packaging for instant recycling guidance.</p>
          </div>
          <button v-if="scanResult" @click="reset" class="px-4 py-2 text-sm font-medium text-emerald-600 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors">
            Scan Another
          </button>
        </header>

        <div v-if="!scanResult" class="max-w-md mx-auto">
          <!-- Type Selector -->
          <div class="flex p-1 bg-gray-200 rounded-xl mb-6">
            <button 
              @click="scanType = 'receipt'" 
              class="flex-1 py-2 text-sm font-medium rounded-lg flex justify-center items-center transition-all"
              :class="scanType === 'receipt' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'"
            >
              <Receipt class="w-4 h-4 mr-2" /> Receipt
            </button>
            <button 
              @click="scanType = 'packaging'" 
              class="flex-1 py-2 text-sm font-medium rounded-lg flex justify-center items-center transition-all"
              :class="scanType === 'packaging' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'"
            >
              <Box class="w-4 h-4 mr-2" /> Material
            </button>
            <button 
              @click="scanType = 'barcode'" 
              class="flex-1 py-2 text-sm font-medium rounded-lg flex justify-center items-center transition-all"
              :class="scanType === 'barcode' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'"
            >
              <Barcode class="w-4 h-4 mr-2" /> Barcode
            </button>
          </div>

          <!-- Camera Component -->
          <ScannerCapture :isProcessing="isProcessing" @capture="handleCapture" />
          
          <!-- Global Error -->
          <div v-if="errorMsg" class="mt-4 p-4 bg-red-50 rounded-xl flex items-start text-red-800 border border-red-100">
            <AlertTriangle class="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
            <p class="text-sm">{{ errorMsg }}</p>
          </div>
        </div>

        <!-- Results View -->
        <div v-else class="space-y-6">
          <div v-if="scanType === 'receipt' && scanResult.items" class="space-y-4">
            <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 mb-6 flex justify-between items-center">
              <div>
                <h3 class="font-bold text-gray-900">{{ scanResult.store_name || 'Receipt Analysis' }}</h3>
                <p class="text-sm text-gray-500">{{ scanResult.date || 'Recent trip' }}</p>
              </div>
              <div class="text-right">
                <div class="text-2xl font-black text-emerald-600">{{ scanResult.trip_sustainability_score }}/10</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-widest">Eco Score</div>
              </div>
            </div>
            
            <ScanResultCard v-for="(item, i) in scanResult.items" :key="i" :result="item" />
          </div>

          <div v-else>
            <!-- Single item response (Barcode/Packaging) -->
            <ScanResultCard :result="scanResult" />
          </div>
        </div>

      </div>
    </main>
  </div>
</template>
