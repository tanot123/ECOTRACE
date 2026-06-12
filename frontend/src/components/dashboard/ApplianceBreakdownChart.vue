<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  data: Array<{ name: string; kwh: number; percentage: number }>
}>()

const chartData = computed(() => {
  return {
    labels: props.data.map(d => d.name),
    datasets: [
      {
        backgroundColor: [
          '#10B981', // Emerald 500
          '#3B82F6', // Blue 500
          '#F59E0B', // Amber 500
          '#8B5CF6', // Violet 500
          '#9CA3AF'  // Gray 400
        ],
        borderWidth: 0,
        hoverOffset: 4,
        data: props.data.map(d => d.kwh)
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '75%',
  plugins: {
    legend: {
      position: 'right' as const,
      labels: {
        usePointStyle: true,
        padding: 20,
        color: '#4B5563',
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: '#1f2937',
      padding: 12,
      callbacks: {
        label: function(context: any) {
          const item = props.data[context.dataIndex]
          return ` ${item.kwh} kWh (${item.percentage}%)`
        }
      }
    }
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm w-full h-full flex flex-col">
    <h3 class="text-base font-semibold text-gray-900 mb-4">Appliance Breakdown</h3>
    <div class="flex-grow relative min-h-[250px]">
      <Doughnut :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
