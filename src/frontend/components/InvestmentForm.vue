<template>
  <div class="investment-form">
    <h2>Create New Investment</h2>
    <form @submit.prevent="createInvestment" class="form">
      <div class="form-group">
        <label for="amount">Investment Amount ($)</label>
        <input
          type="number"
          id="amount"
          v-model="formData.amount"
          min="100"
          required
          class="form-control"
          :class="{ 'is-invalid': errors.amount }"
        />
        <div class="invalid-feedback" v-if="errors.amount">
          {{ errors.amount }}
        </div>
        <small class="text-muted">Minimum investment: $100</small>
      </div>

      <div class="form-group">
        <label for="duration">Duration (days)</label>
        <input
          type="number"
          id="duration"
          v-model="formData.duration"
          min="30"
          max="365"
          required
          class="form-control"
          :class="{ 'is-invalid': errors.duration }"
        />
        <div class="invalid-feedback" v-if="errors.duration">
          {{ errors.duration }}
        </div>
        <small class="text-muted">Duration between 30 and 365 days</small>
      </div>

      <div class="investment-summary" v-if="formData.amount && formData.duration">
        <h3>Investment Summary</h3>
        <p>Amount: ${{ formData.amount }}</p>
        <p>Duration: {{ formData.duration }} days</p>
        <p>Interest Rate: {{ interestRate }}%</p>
        <p>Expected Return: ${{ expectedReturn }}</p>
      </div>

      <button type="submit" class="btn btn-primary" :disabled="loading">
        {{ loading ? 'Creating Investment...' : 'Create Investment' }}
      </button>
    </form>

    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'InvestmentForm',
  setup() {
    const store = useStore()
    const formData = ref({
      amount: '',
      duration: ''
    })
    const errors = ref({})
    const loading = ref(false)
    const error = ref(null)
    const interestRate = 10 // Default interest rate

    const expectedReturn = computed(() => {
      if (!formData.value.amount || !formData.value.duration) return 0
      const principal = parseFloat(formData.value.amount)
      const days = parseFloat(formData.value.duration)
      const interest = (principal * interestRate * days) / (365 * 100)
      return (principal + interest).toFixed(2)
    })

    const validateForm = () => {
      errors.value = {}
      if (!formData.value.amount || formData.value.amount < 100) {
        errors.value.amount = 'Investment amount must be at least $100'
      }
      if (!formData.value.duration || formData.value.duration < 30 || formData.value.duration > 365) {
        errors.value.duration = 'Duration must be between 30 and 365 days'
      }
      return Object.keys(errors.value).length === 0
    }

    const createInvestment = async () => {
      if (!validateForm()) return

      loading.value = true
      error.value = null

      try {
        await store.dispatch('investments/createInvestment', formData.value)
        formData.value = { amount: '', duration: '' }
        store.dispatch('investments/fetchInvestments')
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to create investment'
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      errors,
      loading,
      error,
      interestRate,
      expectedReturn,
      createInvestment
    }
  }
}
</script>

<style scoped>
.investment-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.investment-summary {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 1rem;
}
</style> 