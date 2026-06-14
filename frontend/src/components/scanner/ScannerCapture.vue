<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { Camera, Upload, X, Check } from 'lucide-vue-next'

const props = defineProps<{
  isProcessing: boolean
}>()

const emit = defineEmits<{
  (e: 'capture', file: File): void
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const stream = ref<MediaStream | null>(null)
const capturedImage = ref<string | null>(null)
const errorMsg = ref('')

const startCamera = async () => {
  errorMsg.value = ''
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value
    }
  } catch (err: any) {
    console.error("Camera error:", err)
    errorMsg.value = "Camera access denied or unavailable. Please use file upload."
  }
}

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
}

const capture = () => {
  if (videoRef.value && canvasRef.value) {
    const video = videoRef.value
    const canvas = canvasRef.value
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      capturedImage.value = canvas.toDataURL('image/jpeg', 0.8)
      stopCamera()
    }
  }
}

const retake = () => {
  capturedImage.value = null
  startCamera()
}

const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const reader = new FileReader()
    reader.onload = (e) => {
      capturedImage.value = e.target?.result as string
    }
    reader.readAsDataURL(input.files[0])
    stopCamera()
  }
}

const confirm = () => {
  if (capturedImage.value) {
    // Convert data URL to Blob -> File
    fetch(capturedImage.value)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], "scan.jpg", { type: "image/jpeg" })
        emit('capture', file)
      })
  }
}

// Start camera by default if not captured
if (!capturedImage.value) {
  startCamera()
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<template>
  <div class="bg-gray-900 rounded-2xl overflow-hidden shadow-xl max-w-md mx-auto">
    <div v-if="errorMsg" class="p-4 bg-red-900 text-red-200 text-sm">
      {{ errorMsg }}
    </div>

    <div class="relative bg-black aspect-[3/4] flex items-center justify-center">
      <!-- Preview Mode -->
      <template v-if="capturedImage">
        <img :src="capturedImage" class="w-full h-full object-cover" />
      </template>
      
      <!-- Live Camera Mode -->
      <template v-else>
        <video 
          ref="videoRef" 
          autoplay 
          playsinline 
          class="w-full h-full object-cover"
          v-show="stream"
        ></video>
        <canvas ref="canvasRef" class="hidden"></canvas>
        <div v-if="!stream && !errorMsg" class="text-gray-400 flex flex-col items-center">
          <span class="animate-pulse">Starting camera...</span>
        </div>
      </template>
      
      <!-- Processing Overlay -->
      <div v-if="isProcessing" class="absolute inset-0 bg-black/60 flex flex-col items-center justify-center z-10 backdrop-blur-sm">
        <div class="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-white font-medium animate-pulse">Gemini is analyzing...</p>
      </div>
    </div>

    <!-- Controls -->
    <div class="p-4 bg-gray-900 flex justify-center gap-4" :class="{ 'opacity-50 pointer-events-none': isProcessing }">
      <template v-if="capturedImage">
        <button @click="retake" class="flex-1 py-3 px-4 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-medium flex items-center justify-center transition-colors">
          <X class="w-5 h-5 mr-2" /> Retake
        </button>
        <button @click="confirm" class="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium flex items-center justify-center transition-colors">
          <Check class="w-5 h-5 mr-2" /> Use Photo
        </button>
      </template>
      
      <template v-else>
        <label class="flex-1 py-3 px-4 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-xl font-medium flex items-center justify-center cursor-pointer transition-colors border border-gray-700">
          <Upload class="w-5 h-5 mr-2" /> Upload
          <input type="file" accept="image/*" class="hidden" @change="handleFileUpload" />
        </label>
        <button v-if="stream" @click="capture" class="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium flex items-center justify-center transition-colors">
          <Camera class="w-5 h-5 mr-2" /> Capture
        </button>
      </template>
    </div>
  </div>
</template>
