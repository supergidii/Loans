<template>
  <div class="investment-list">
    <div class="stats-container">
      <h2>Investment Statistics</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Active Investments</h3>
          <p class="stat-value">{{ stats.activeInvestments }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Active Amount</h3>
          <p class="stat-value">${{ stats.totalActiveAmount }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Earnings</h3>
          <p class="stat-value">${{ stats.totalEarnings }}</p>
        </div>
        <div class="stat-card">
          <h3>Referral Earnings</h3>
          <p class="stat-value">${{ stats.referralEarnings }}</p>
        </div>
      </div>
    </div>

    <div class="investments-container">
      <h2>Your Investments</h2>
      <div v-if="loading" class="loading">
        Loading investments...
      </div>
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      <div v-else-if="investments.length === 0" class="no-investments">
        You haven't made any investments yet.
      </div>
      <div v-else class="investments-grid">
        <div v-for="investment in investments" :key="investment._id" class="investment-card">
          <div class="investment-header">
            <h3>Investment #{{ investment._id.slice(-4) }}</h3>
            <span :class="['status-badge', investment.status]">
              {{ investment.status }}
            </span>
          </div>
          <div class="investment-details">
            <p><strong>Amount:</strong> ${{ investment.amount }}</p>
            <p><strong>Duration:</strong> {{ investment.duration }} days</p>
            <p><strong>Start Date:</strong> {{ formatDate(investment.startDate) }}</p>
            <p><strong>End Date:</strong> {{ formatDate(investment.endDate) }}</p>
            <p><strong>Interest Rate:</strong> {{ investment.interestRate }}%</p>
            <p><strong>Expected Return:</strong> ${{ investment.expectedReturn }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'InvestmentList',
  setup() {
    const store = useStore()
    const loading = ref(true)
    const error = ref(null)

    const investments = computed(() => store.getters['investments/allInvestments'])
    const stats = computed(() => store.getters['investments/investmentStats'])

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const fetchInvestments = async () => {
      loading.value = true
      error.value = null
      try {
        await store.dispatch('investments/fetchInvestments')
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to fetch investments'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchInvestments()
    })

    return {
      investments,
      stats,
      loading,
      error,
      formatDate,
      fetchInvestments
    }
  }
}
</script>

<style scoped>
.investment-list {
  padding: 20px;
}

.stats-container {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.stat-card {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #007bff;
  margin: 0.5rem 0;
}

.investments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.investment-card {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
}

.investment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.completed {
  background-color: #cce5ff;
  color: #004085;
}

.investment-details p {
  margin: 0.5rem 0;
}

.loading, .error, .no-investments {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #dc3545;
}
</style> 