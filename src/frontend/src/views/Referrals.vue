<template>
  <div class="referrals-container">
    <ReferralLink />
    
    <div class="referrals-list">
      <div class="referrals-header">
        <h2>Your Referrals</h2>
        <div class="view-toggle">
          <button 
            @click="viewMode = 'cards'" 
            :class="['toggle-btn', { active: viewMode === 'cards' }]"
          >
            <i class="fas fa-th-large"></i> Cards
          </button>
          <button 
            @click="viewMode = 'table'" 
            :class="['toggle-btn', { active: viewMode === 'table' }]"
          >
            <i class="fas fa-table"></i> Table
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        Loading referrals...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="!referrals.length" class="no-referrals">
        <p>You haven't referred anyone yet.</p>
        <p>Share your referral link to start earning!</p>
      </div>
      
      <!-- Card View -->
      <div v-else-if="viewMode === 'cards'" class="referrals-grid">
        <div v-for="referral in referrals" :key="referral._id" class="referral-card">
          <div class="referral-header">
            <h3>{{ referral.referred.username }}</h3>
            <span :class="['status-badge', referral.status]">
              {{ referral.status }}
            </span>
          </div>
          
          <div class="referral-details">
            <div class="detail-item">
              <span class="label">Joined:</span>
              <span class="value">{{ formatDate(referral.createdAt) }}</span>
            </div>
            
            <div class="detail-item">
              <span class="label">Commission Rate:</span>
              <span class="value">{{ referral.commissionRate }}%</span>
            </div>
            
            <div class="detail-item">
              <span class="label">Total Commission:</span>
              <span class="value">${{ referral.commission.toFixed(2) }}</span>
            </div>
            
            <div class="detail-item">
              <span class="label">Payment Status:</span>
              <span :class="['value', 'payment-status', referral.paymentStatus]">
                {{ referral.paymentStatus }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Table View -->
      <div v-else class="referrals-table-container">
        <table class="referrals-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Status</th>
              <th>Joined Date</th>
              <th>Commission Rate</th>
              <th>Commission</th>
              <th>Payment Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="referral in referrals" :key="referral._id">
              <td>{{ referral.referred.username }}</td>
              <td>
                <span :class="['status-badge', referral.status]">
                  {{ referral.status }}
                </span>
              </td>
              <td>{{ formatDate(referral.createdAt) }}</td>
              <td>{{ referral.commissionRate }}%</td>
              <td>${{ referral.commission.toFixed(2) }}</td>
              <td>
                <span :class="['payment-status', referral.paymentStatus]">
                  {{ referral.paymentStatus }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import ReferralLink from '@/components/ReferralLink.vue'

export default {
  name: 'Referrals',
  components: {
    ReferralLink
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const error = ref(null)
    const viewMode = ref('cards')

    const referrals = computed(() => store.state.referrals.referrals)

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const fetchReferrals = async () => {
      try {
        loading.value = true
        error.value = null
        await store.dispatch('referrals/fetchReferrals')
      } catch (err) {
        console.error('Error fetching referrals:', err)
        error.value = 'Failed to load referrals'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchReferrals()
    })

    return {
      loading,
      error,
      referrals,
      formatDate,
      viewMode
    }
  }
}
</script>

<style scoped>
.referrals-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.referrals-list {
  margin-top: 40px;
}

.referrals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h2 {
  color: #2c3e50;
  margin: 0;
}

.view-toggle {
  display: flex;
  gap: 10px;
}

.toggle-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: #f8f9fa;
}

.toggle-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.loading, .error, .no-referrals {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #dc3545;
}

.no-referrals p {
  margin: 10px 0;
}

/* Card View Styles */
.referrals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.referral-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.referral-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.referral-header h3 {
  margin: 0;
  color: #2c3e50;
}

/* Table View Styles */
.referrals-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.referrals-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.referrals-table th,
.referrals-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.referrals-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

.referrals-table tr:hover {
  background: #f8f9fa;
}

/* Common Styles */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: 500;
}

.status-badge.pending {
  background: #ffeeba;
  color: #856404;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.completed {
  background: #cce5ff;
  color: #004085;
}

.referral-details {
  display: grid;
  gap: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #666;
  font-size: 0.9em;
}

.value {
  font-weight: 500;
  color: #2c3e50;
}

.payment-status {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8em;
}

.payment-status.pending {
  background: #fff3cd;
  color: #856404;
}

.payment-status.paid {
  background: #d4edda;
  color: #155724;
}

.payment-status.failed {
  background: #f8d7da;
  color: #721c24;
}

@media (max-width: 768px) {
  .referrals-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .view-toggle {
    width: 100%;
  }
  
  .toggle-btn {
    flex: 1;
    justify-content: center;
  }
}
</style> 