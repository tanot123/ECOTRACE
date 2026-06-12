import { defineStore } from 'pinia'
import api from '../services/api'

export interface DashboardSummary {
  green_score: {
    current: number
    trend: string
    change_from_last_week: number
  }
  impact: {
    co2_reduced_kg: number
    water_saved_liters: number
    money_saved_usd: number
    trees_equivalent: number
  }
  energy: {
    today_kwh: number
    week_total_kwh: number
    month_total_kwh: number
    daily_trend: Array<{date: string, value: number}>
    by_appliance: Array<{name: string, kwh: number, percentage: number}>
  }
  water: {
    today_liters: number
    week_total_liters: number
    daily_trend: Array<{date: string, value: number}>
  }
  energy_vampires: {
    count: number
    devices: Array<{name: string, standby_watts: number, yearly_cost: number}>
  }
  active_challenges: {
    count: number
    challenges: Array<{id: string, title: string, progress: number, target: number, unit: string}>
  }
}

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    summary: null as DashboardSummary | null,
    isLoading: false,
    error: null as string | null
  }),
  actions: {
    async fetchSummary() {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.get('/dashboard/summary')
        this.summary = response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch dashboard data'
        console.error('Dashboard fetch error:', error)
      } finally {
        this.isLoading = false
      }
    }
  }
})
