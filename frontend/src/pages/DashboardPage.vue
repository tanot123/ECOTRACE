<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { Leaf, Droplets, DollarSign, Activity } from 'lucide-vue-next'
import { useDashboardStore } from '../stores/dashboard'
import Sidebar from '../components/layout/Sidebar.vue'
import StatCard from '../components/dashboard/StatCard.vue'
import GreenScoreGauge from '../components/dashboard/GreenScoreGauge.vue'
import RealTimeMonitor from '../components/dashboard/RealTimeMonitor.vue'
import EnergyTrendChart from '../components/dashboard/EnergyTrendChart.vue'
import ApplianceBreakdownChart from '../components/dashboard/ApplianceBreakdownChart.vue'
import VampireAlert from '../components/dashboard/VampireAlert.vue'
import { useWindowSize } from '@vueuse/core'

const dashboardStore = useDashboardStore()
const { width } = useWindowSize()

const isMobile = computed(() => width.value < 768)

onMounted(() => {
  dashboardStore.fetchSummary()
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden font-sans">
    <Sidebar :isMobile="isMobile" />
    
    <main class="flex-1 overflow-y-auto pb-20 md:pb-0">
      <div class="p-6 md:p-10 max-w-7xl mx-auto space-y-6">
        
        <header class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900">Welcome back!</h2>
          <p class="text-gray-500">Here is your energy and sustainability summary.</p>
        </header>

        <div v-if="dashboardStore.isLoading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
        </div>

        <div v-else-if="dashboardStore.error" class="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200">
          {{ dashboardStore.error }}
        </div>

        <div v-else-if="dashboardStore.summary" class="space-y-6">
          
          <!-- Top Row: Score & Main Stats -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="lg:col-span-1 space-y-6">
              <GreenScoreGauge 
                :score="dashboardStore.summary.green_score.current" 
                :trend="dashboardStore.summary.green_score.trend as any" 
              />
              <RealTimeMonitor />
            </div>
            
            <StatCard 
              title="CO₂ Reduced" 
              :value="`${dashboardStore.summary.impact.co2_reduced_kg} kg`"
              trend="up"
              trendValue="12%"
              colorTheme="emerald"
            >
              <template #icon><Leaf class="w-5 h-5 text-emerald-600" /></template>
            </StatCard>

            <StatCard 
              title="Water Saved" 
              :value="`${dashboardStore.summary.impact.water_saved_liters} L`"
              trend="up"
              trendValue="5%"
              colorTheme="blue"
            >
              <template #icon><Droplets class="w-5 h-5 text-blue-600" /></template>
            </StatCard>

            <StatCard 
              title="Money Saved" 
              :value="`$${dashboardStore.summary.impact.money_saved_usd}`"
              trend="stable"
              trendValue="0%"
              colorTheme="emerald"
            >
              <template #icon><DollarSign class="w-5 h-5 text-emerald-600" /></template>
            </StatCard>
          </div>

          <!-- Middle Row: Charts -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2 min-h-[300px]">
              <EnergyTrendChart :data="dashboardStore.summary.energy.daily_trend" />
            </div>
            <div class="lg:col-span-1 min-h-[300px]">
              <ApplianceBreakdownChart :data="dashboardStore.summary.energy.by_appliance" />
            </div>
          </div>

          <!-- Bottom Row: Vampires & Challenges -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <VampireAlert :vampires="dashboardStore.summary.energy_vampires.devices" />
            
            <!-- Active Challenges Preview -->
            <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
              <div class="flex items-center space-x-2 mb-4">
                <div class="bg-emerald-100 p-2 rounded-lg">
                  <Activity class="w-5 h-5 text-emerald-600" />
                </div>
                <h3 class="text-base font-semibold text-gray-900">Active Challenges</h3>
              </div>
              
              <div class="space-y-4">
                <div v-for="challenge in dashboardStore.summary.active_challenges.challenges" :key="challenge.id" class="space-y-1">
                  <div class="flex justify-between text-sm">
                    <span class="font-medium text-gray-700">{{ challenge.title }}</span>
                    <span class="text-gray-500">{{ challenge.progress }}/{{ challenge.target }} {{ challenge.unit }}</span>
                  </div>
                  <div class="w-full bg-gray-100 rounded-full h-2">
                    <div class="bg-emerald-500 h-2 rounded-full transition-all duration-500" :style="{ width: `${Math.min((challenge.progress / challenge.target) * 100, 100)}%` }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>
