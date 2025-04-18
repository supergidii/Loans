<template>
  <div class="paired-users-container">
    <h2>Paired Users</h2>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading">
      Loading paired users...
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Empty state -->
    <div v-else-if="pairedUsers.length === 0" class="empty-state">
      No paired users found.
    </div>

    <!-- Paired users list -->
    <div v-else class="paired-users-list">
      <div v-for="pair in pairedUsers" :key="pair._id" class="paired-user-card">
        <div class="user-info">
          <div class="user">
            <h3>User 1</h3>
            <p>{{ pair.user1.firstName }} {{ pair.user1.lastName }}</p>
            <p class="email">{{ pair.user1.email }}</p>
          </div>
          <div class="user">
            <h3>User 2</h3>
            <p>{{ pair.user2.firstName }} {{ pair.user2.lastName }}</p>
            <p class="email">{{ pair.user2.email }}</p>
          </div>
        </div>
        
        <div class="pair-details">
          <div class="status" :class="pair.status">
            {{ pair.status }}
          </div>
          <div class="pairing-type">
            Type: {{ pair.pairingType }}
          </div>
          <div class="dates">
            <p>Started: {{ formatDate(pair.startDate) }}</p>
            <p v-if="pair.endDate">Ended: {{ formatDate(pair.endDate) }}</p>
          </div>
          <p v-if="pair.notes" class="notes">
            Notes: {{ pair.notes }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'PairedUsersList',
  setup() {
    const pairedUsers = ref([])
    const loading = ref(true)
    const error = ref(null)

    const fetchPairedUsers = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await axios.get('/api/paired-users/my-pairings')
        pairedUsers.value = response.data.data
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to fetch paired users'
        console.error('Error fetching paired users:', err)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      fetchPairedUsers()
    })

    return {
      pairedUsers,
      loading,
      error,
      formatDate
    }
  }
}
</script>

<style scoped>
.paired-users-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.loading, .error-message, .empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  color: #dc3545;
}

.paired-users-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.paired-user-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 15px;
}

.user h3 {
  font-size: 1rem;
  color: #2c3e50;
  margin-bottom: 5px;
}

.user p {
  margin: 0;
  color: #666;
}

.email {
  font-size: 0.9rem;
  color: #888;
}

.pair-details {
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 10px;
}

.status.pending {
  background-color: #ffeeba;
  color: #856404;
}

.status.active {
  background-color: #d4edda;
  color: #155724;
}

.status.completed {
  background-color: #cce5ff;
  color: #004085;
}

.status.cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.pairing-type {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 10px;
}

.dates {
  font-size: 0.9rem;
  color: #666;
}

.dates p {
  margin: 5px 0;
}

.notes {
  margin-top: 10px;
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
}
</style> 