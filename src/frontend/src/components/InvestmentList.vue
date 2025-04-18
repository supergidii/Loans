<template>
  <div class="investment-list">
    <h2>Your Investments</h2>
    
    <div v-if="loading" class="loading">
      Loading investments...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="investments.length === 0" class="no-investments">
      No investments found. Start investing today!
    </div>
    
    <div v-else class="table-container">
      <table class="investments-table">
        <thead>
          <tr>
            <th>Amount</th>
            <th>Duration</th>
            <th>Interest Rate</th>
            <th>Expected Return</th>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="investment in investments" :key="investment._id">
            <td>${{ investment.amount.toFixed(2) }}</td>
            <td>{{ investment.duration }} days</td>
            <td>{{ investment.interestRate }}%</td>
            <td>${{ investment.expectedReturn.toFixed(2) }}</td>
            <td>{{ new Date(investment.startDate).toLocaleDateString() }}</td>
            <td>{{ new Date(investment.endDate).toLocaleDateString() }}</td>
            <td>
              <span :class="['status-badge', investment.status.toLowerCase()]">
                {{ investment.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="investment-stats" v-if="investments && investments.length > 0">
      <h3>Investment Statistics</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <h4>Total Invested</h4>
          <p>${{ totalInvested }}</p>
        </div>
        <div class="stat-card">
          <h4>Expected Returns</h4>
          <p>${{ totalExpectedReturns }}</p>
        </div>
        <div class="stat-card">
          <h4>Active Investments</h4>
          <p>{{ activeInvestments }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'InvestmentList',
  setup() {
    const store = useStore()

    const investments = computed(() => store.state.investments.investments || [])
    const loading = computed(() => store.state.investments.loading)
    const error = computed(() => store.state.investments.error)

    const totalInvested = computed(() => {
      if (!investments.value) return '0.00'
      return investments.value.reduce((sum, inv) => sum + (inv.amount || 0), 0).toFixed(2)
    })

    const totalExpectedReturns = computed(() => {
      if (!investments.value) return '0.00'
      return investments.value.reduce((sum, inv) => sum + (inv.expectedReturn || 0), 0).toFixed(2)
    })

    const activeInvestments = computed(() => {
      if (!investments.value) return 0
      return investments.value.filter(inv => inv.status.toLowerCase() === 'active').length
    })

    const fetchInvestments = async () => {
      try {
        await store.dispatch('investments/fetchInvestments')
      } catch (error) {
        console.error('Failed to fetch investments:', error)
      }
    }

    onMounted(() => {
      fetchInvestments()
    })

    return {
      investments,
      loading,
      error,
      totalInvested,
      totalExpectedReturns,
      activeInvestments,
      fetchInvestments
    }
  }
}
</script>

<style scoped>
.investment-list {
  padding: 20px;
}

.loading, .error, .no-investments {
  text-align: center;
  padding: 20px;
  font-size: 1.1em;
}

.error {
  color: #dc3545;
}

.table-container {
  overflow-x: auto;
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.investments-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.investments-table th,
.investments-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.investments-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.investments-table tr:hover {
  background-color: #f9fafb;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  font-weight: 500;
  display: inline-block;
}

.status-badge.active {
  background-color: #e3fcef;
  color: #0a6c3b;
}

.status-badge.completed {
  background-color: #e7f5ff;
  color: #0c63e4;
}

.status-badge.cancelled {
  background-color: #fee2e2;
  color: #dc2626;
}

.status-badge.pending {
  background-color: #fff7ed;
  color: #c2410c;
}

.investment-stats {
  margin-top: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h4 {
  margin: 0 0 10px 0;
  color: #6b7280;
  font-size: 0.9em;
}

.stat-card p {
  margin: 0;
  font-size: 1.5em;
  font-weight: 600;
  color: #111827;
}
</style> 