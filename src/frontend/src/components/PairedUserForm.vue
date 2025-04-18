<template>
  <div class="paired-user-form">
    <h2>Create New Pairing</h2>
    
    <form @submit.prevent="handleSubmit" class="form">
      <div class="form-group">
        <label for="user1">User 1</label>
        <select 
          id="user1" 
          v-model="formData.user1" 
          required
          class="form-control"
        >
          <option value="">Select User 1</option>
          <option v-for="user in users" :key="user._id" :value="user._id">
            {{ user.firstName }} {{ user.lastName }} ({{ user.email }})
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="user2">User 2</label>
        <select 
          id="user2" 
          v-model="formData.user2" 
          required
          class="form-control"
        >
          <option value="">Select User 2</option>
          <option v-for="user in users" :key="user._id" :value="user._id">
            {{ user.firstName }} {{ user.lastName }} ({{ user.email }})
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="pairingType">Pairing Type</label>
        <select 
          id="pairingType" 
          v-model="formData.pairingType" 
          required
          class="form-control"
        >
          <option value="">Select Type</option>
          <option value="investment">Investment</option>
          <option value="referral">Referral</option>
          <option value="manual">Manual</option>
        </select>
      </div>

      <div class="form-group">
        <label for="notes">Notes (Optional)</label>
        <textarea 
          id="notes" 
          v-model="formData.notes" 
          class="form-control"
          rows="3"
          placeholder="Add any additional notes about this pairing"
        ></textarea>
      </div>

      <div class="form-actions">
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="loading"
        >
          {{ loading ? 'Creating...' : 'Create Pairing' }}
        </button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script>
import { ref, onMounted, defineEmits } from 'vue'
import axios from 'axios'

export default {
  name: 'PairedUserForm',
  setup() {
    const users = ref([])
    const loading = ref(false)
    const error = ref(null)
    const formData = ref({
      user1: '',
      user2: '',
      pairingType: '',
      notes: ''
    })

    // Define the emit function using defineEmits
    const emit = defineEmits(['pairing-created'])

    const fetchUsers = async () => {
      try {
        const response = await axios.get('/api/admin/users')
        users.value = response.data.data
      } catch (err) {
        console.error('Error fetching users:', err)
        error.value = 'Failed to fetch users list'
      }
    }

    const handleSubmit = async () => {
      try {
        loading.value = true
        error.value = null

        // Validate that user1 and user2 are different
        if (formData.value.user1 === formData.value.user2) {
          error.value = 'Cannot pair a user with themselves'
          return
        }

        const response = await axios.post('/api/paired-users', formData.value)
        
        // Reset form
        formData.value = {
          user1: '',
          user2: '',
          pairingType: '',
          notes: ''
        }

        // Emit success event
        emit('pairing-created', response.data.data)
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to create pairing'
        console.error('Error creating pairing:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchUsers()
    })

    return {
      users,
      loading,
      error,
      formData,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.paired-user-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #2c3e50;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  margin-top: 20px;
  text-align: right;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  font-size: 0.9rem;
}
</style> 