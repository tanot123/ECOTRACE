<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps<{
  data: Array<{ date: string; value: number }>
}>()

const chartData = computed(() => {
  return {
    labels: props.data.map(d => {
      const date = new Date(d.date)
      return date.toLocaleDateString('en-US', { weekday: 'short' })
    }),
    datasets: [
      {
        label: 'Energy Usage (kWh)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderColor: '#10B981',
        pointBackgroundColor: '#ffffff',
        pointBorderColor: '#10B981',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: true,
        data: props.data.map(d => d.value),
        tension: 0.4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 800
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: '#1f2937',
      padding: 12,
      titleFont: { size: 13 },
      bodyFont: { size: 14, weight: 'bold' as const },
      displayColors: false,
      callbacks: {
        label: function(context: any) {
          return `${context.parsed.y} kWh`
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#f3f4f6',
        drawBorder: false
      },
      ticks: {
        color: '#6b7280'
      }
    },
    x: {
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        color: '#6b7280'
      }
    }
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm w-full h-full flex flex-col">
    <h3 class="text-base font-semibold text-gray-900 mb-4">Energy Usage Trend</h3>
    <div class="flex-grow relative min-h-[250px]">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
