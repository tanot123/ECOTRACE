<script setup lang="ts">
import { Recycle, Trash2, Leaf, AlertTriangle, AlertCircle } from 'lucide-vue-next'

const props = defineProps<{
  result: any
}>()

const getBinColorClass = (color: string) => {
  switch(color?.toLowerCase()) {
    case 'blue': return 'bg-blue-100 text-blue-700 border-blue-200'
    case 'green': return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    case 'black': return 'bg-gray-800 text-gray-200 border-gray-700'
    case 'special': return 'bg-amber-100 text-amber-700 border-amber-200'
    default: return 'bg-gray-100 text-gray-700 border-gray-200'
  }
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    
    <!-- Receipt Item -->
    <div v-if="result.packaging_type" class="p-5">
      <div class="flex justify-between items-start mb-3">
        <div>
          <h4 class="font-bold text-gray-900 text-lg">{{ result.name }}</h4>
          <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">{{ result.packaging_type.replace('_', ' ') }}</span>
        </div>
        <div class="px-3 py-1 rounded-full text-xs font-bold border flex items-center capitalize" :class="getBinColorClass(result.bin_color)">
          <div class="w-2 h-2 rounded-full mr-1.5" :class="{'bg-blue-500': result.bin_color==='blue', 'bg-emerald-500': result.bin_color==='green', 'bg-gray-500': result.bin_color==='black', 'bg-amber-500': result.bin_color==='special'}"></div>
          {{ result.bin_color }} Bin
        </div>
      </div>
      
      <div class="flex items-center space-x-4 mb-4 text-sm">
        <span v-if="result.recyclable" class="flex items-center text-emerald-600 font-medium"><Recycle class="w-4 h-4 mr-1" /> Recyclable</span>
        <span v-else-if="result.compostable" class="flex items-center text-emerald-600 font-medium"><Leaf class="w-4 h-4 mr-1" /> Compostable</span>
        <span v-else class="flex items-center text-red-600 font-medium"><Trash2 class="w-4 h-4 mr-1" /> Landfill</span>
      </div>

      <div class="bg-blue-50 rounded-lg p-3 text-sm text-blue-800 border border-blue-100">
        <p class="font-medium flex items-center mb-1"><AlertCircle class="w-4 h-4 mr-1.5"/> Disposal Instruction</p>
        <p>{{ result.recycling_instruction }}</p>
      </div>
      
      <div v-if="result.eco_tip" class="mt-3 text-sm text-emerald-700 flex items-start">
        <Leaf class="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" />
        <p><i>Tip:</i> {{ result.eco_tip }}</p>
      </div>
    </div>

    <!-- Packaging/Barcode Result (Single item returned directly) -->
    <div v-else class="p-5">
      <div class="flex justify-between items-start mb-3">
        <div>
          <h4 class="font-bold text-gray-900 text-lg">{{ result.product_name || result.material_name }}</h4>
          <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">{{ result.category || result.material_type?.replace('_', ' ') }}</span>
        </div>
        <div class="px-3 py-1 rounded-full text-xs font-bold border flex items-center capitalize" :class="getBinColorClass(result.bin_color)">
          <div class="w-2 h-2 rounded-full mr-1.5" :class="{'bg-blue-500': result.bin_color==='blue', 'bg-emerald-500': result.bin_color==='green', 'bg-gray-500': result.bin_color==='black', 'bg-amber-500': result.bin_color==='special'}"></div>
          {{ result.bin_color }} Bin
        </div>
      </div>
      
      <div class="flex items-center space-x-4 mb-4 text-sm">
        <span v-if="result.recyclable || result.overall_recyclable" class="flex items-center text-emerald-600 font-medium"><Recycle class="w-4 h-4 mr-1" /> Recyclable</span>
        <span v-else-if="result.compostable" class="flex items-center text-emerald-600 font-medium"><Leaf class="w-4 h-4 mr-1" /> Compostable</span>
        <span v-else class="flex items-center text-red-600 font-medium"><Trash2 class="w-4 h-4 mr-1" /> Landfill</span>
      </div>

      <!-- Multiple instructions (Packaging) -->
      <div v-if="result.disposal_instructions" class="bg-blue-50 rounded-lg p-3 text-sm text-blue-800 border border-blue-100">
        <p class="font-medium flex items-center mb-1"><AlertCircle class="w-4 h-4 mr-1.5"/> Disposal Instructions</p>
        <ul class="list-disc pl-5 space-y-1">
          <li v-for="(inst, i) in result.disposal_instructions" :key="i">{{ inst }}</li>
        </ul>
      </div>

      <!-- Multiple components (Barcode) -->
      <div v-if="result.packaging_materials" class="bg-gray-50 rounded-lg p-3 text-sm text-gray-800 border border-gray-200">
        <p class="font-medium flex items-center mb-2"><AlertCircle class="w-4 h-4 mr-1.5 text-gray-500"/> Components</p>
        <div v-for="(comp, i) in result.packaging_materials" :key="i" class="mb-2 pb-2 border-b border-gray-200 last:border-0 last:mb-0 last:pb-0">
          <span class="font-bold capitalize">{{ comp.component }} ({{ comp.material }}):</span> 
          <span :class="comp.recyclable ? 'text-emerald-600' : 'text-red-600'">{{ comp.instruction }}</span>
        </div>
      </div>
      
      <div v-if="result.environmental_impact" class="mt-4 bg-emerald-50 rounded-lg p-3 border border-emerald-100">
        <p class="text-sm font-bold text-emerald-800 mb-1 flex items-center"><Leaf class="w-4 h-4 mr-1"/> Environmental Impact</p>
        <p class="text-xs text-emerald-700 mb-1"><b>Decomposition:</b> {{ result.environmental_impact.decomposition_time }}</p>
        <p class="text-xs text-emerald-700"><b>Fact:</b> {{ result.environmental_impact.fun_fact }}</p>
      </div>

      <div v-if="result.eco_rating" class="mt-4 flex items-center justify-between border-t pt-3">
        <span class="text-sm font-bold text-gray-700">Eco Rating</span>
        <div class="flex text-emerald-500">
          <Leaf v-for="n in result.eco_rating" :key="`f-${n}`" class="w-4 h-4 fill-current" />
          <Leaf v-for="n in 5 - result.eco_rating" :key="`e-${n}`" class="w-4 h-4 opacity-30" />
        </div>
      </div>
    </div>
  </div>
</template>
