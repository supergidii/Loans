<template>
  <div class="investment-form">
    <h2>Create Investment</h2>
    <form @submit.prevent="createInvestment">
      <div class="form-group">
        <label for="amount">Investment Amount ($)</label>
        <input
          type="number"
          id="amount"
          v-model="formData.amount"
          min="100"
          step="1"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="duration">Duration</label>
        <select
          id="duration"
          v-model="formData.duration"
          required
        >
          <option v-for="option in durationOptions" 
                  :key="option.value" 
                  :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <div class="summary" v-if="expectedReturn">
        <h3>Investment Summary</h3>
        <p>Amount: ${{ formData.amount }}</p>
        <p>Duration: {{ formData.duration }} days</p>
        <p>Expected Return: ${{ expectedReturn.toFixed(2) }}</p>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Creating...' : 'Create Investment' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import api from '../api';

export default {
  name: 'InvestmentForm',
  emits: ['investment-created'],
  setup(props, { emit }) {
    const formData = ref({
      amount: 100,
      duration: 30
    });

    const loading = ref(false);
    const error = ref('');
    const interestRate = 10; // 10% annual interest rate

    const durationOptions = [
      { value: 4, label: '4 days' },
      { value: 8, label: '8 days' },
      { value: 16, label: '16 days' },
      { value: 30, label: '30 days' }
    ];

    const expectedReturn = computed(() => {
      const dailyRate = 0.01; // 1% per day
      return formData.value.amount * (1 + (dailyRate * formData.value.duration));
    });

    const createInvestment = async () => {
      try {
        loading.value = true;
        error.value = '';

        // Validate amount
        if (formData.value.amount < 100) {
          error.value = 'Investment amount must be at least $100';
          return;
        }

        // Validate duration
        if (![4, 8, 16, 30].includes(Number(formData.value.duration))) {
          error.value = 'Duration must be either 4, 8, 16, or 30 days';
          return;
        }

        console.log('Creating investment with data:', formData.value);
        const response = await api.post('/api/investments', {
          amount: Number(formData.value.amount),
          duration: Number(formData.value.duration)
        });
        
        if (response.data.success) {
          // Reset form
          formData.value = {
            amount: 100,
            duration: 30
          };
          
          // Emit success event
          emit('investment-created', response.data.data);
        }
      } catch (err) {
        console.error('Investment creation error:', err);
        error.value = err.response?.data?.message || 'Failed to create investment';
      } finally {
        loading.value = false;
      }
    };

    return {
      formData,
      loading,
      error,
      interestRate,
      durationOptions,
      expectedReturn,
      createInvestment
    };
  }
};
</script>

<style scoped>
.investment-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.duration-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-top: 10px;
}

.duration-option {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.duration-option:hover {
  border-color: #007bff;
}

.duration-option.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.investment-summary {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
  margin: 20px 0;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
}

.summary-item.highlight {
  font-weight: bold;
  color: #28a745;
  font-size: 1.1em;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:hover {
  background: #0069d9;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}
</style> 