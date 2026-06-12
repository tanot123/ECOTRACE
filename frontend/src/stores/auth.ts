import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import type { AxiosError } from 'axios'

export interface User {
  id: string
  email: string
  display_name: string
  green_score: number
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('ecotrace_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => token.value !== null)

  const initialize = async () => {
    if (token.value) {
      await fetchUser()
    }
  }

  const fetchUser = async () => {
    isLoading.value = true
    try {
      const response = await api.get('/users/me')
      user.value = response.data
      error.value = null
    } catch (err) {
      const axiosError = err as AxiosError
      if (axiosError.response?.status === 401) {
        logout()
      } else {
        error.value = 'Failed to fetch user profile'
      }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: any) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/register', data)
      token.value = response.data.access_token
      user.value = response.data.user
      localStorage.setItem('ecotrace_token', response.data.access_token)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const login = async (data: any) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/login', data)
      token.value = response.data.access_token
      user.value = response.data.user
      localStorage.setItem('ecotrace_token', response.data.access_token)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('ecotrace_token')
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    initialize,
    fetchUser,
    register,
    login,
    logout
  }
})
