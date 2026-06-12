<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const displayName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const validationError = ref('')

const handleRegister = async () => {
  validationError.value = ''
  
  if (password.value !== confirmPassword.value) {
    validationError.value = "Passwords do not match."
    return
  }
  
  if (password.value.length < 8) {
    validationError.value = "Password must be at least 8 characters."
    return
  }

  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      display_name: displayName.value
    })
    router.push('/dashboard')
  } catch (err) {
    // Error is handled by the store
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create a new account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Already have an account?
          <router-link to="/login" class="font-medium text-emerald-600 hover:text-emerald-500">
            Sign in here
          </router-link>
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm space-y-4">
          <div>
            <label for="display-name" class="block text-sm font-medium text-gray-700">Display Name</label>
            <input id="display-name" name="display-name" type="text" required v-model="displayName" minlength="2" maxlength="50"
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 focus:z-10 sm:text-sm mt-1"
              placeholder="Your name">
          </div>
          <div>
            <label for="email-address" class="block text-sm font-medium text-gray-700">Email address</label>
            <input id="email-address" name="email" type="email" autocomplete="email" required v-model="email"
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 focus:z-10 sm:text-sm mt-1"
              placeholder="Email address">
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input id="password" name="password" type="password" autocomplete="new-password" required v-model="password"
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 focus:z-10 sm:text-sm mt-1"
              placeholder="Password (min 8 chars)">
          </div>
          <div>
            <label for="confirm-password" class="block text-sm font-medium text-gray-700">Confirm Password</label>
            <input id="confirm-password" name="confirm-password" type="password" autocomplete="new-password" required v-model="confirmPassword"
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 focus:z-10 sm:text-sm mt-1"
              placeholder="Confirm password">
          </div>
        </div>

        <div v-if="validationError || authStore.error" class="text-red-500 text-sm text-center bg-red-50 p-2 rounded">
          {{ validationError || authStore.error }}
        </div>

        <div>
          <button type="submit" :disabled="authStore.isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 transition-colors">
            {{ authStore.isLoading ? 'Creating account...' : 'Create Account' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
