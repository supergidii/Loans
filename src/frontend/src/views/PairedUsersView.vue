<template>
  <div class="paired-users-view">
    <div class="header">
      <h1>Paired Users Management</h1>
      <button 
        v-if="isAdmin" 
        @click="showForm = !showForm"
        class="btn btn-primary"
      >
        {{ showForm ? 'Hide Form' : 'Create New Pairing' }}
      </button>
    </div>

    <PairedUserForm 
      v-if="showForm && isAdmin"
      @pairing-created="handlePairingCreated"
    />

    <PairedUsersList 
      ref="pairedUsersList"
      class="mt-4"
    />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import PairedUsersList from '@/components/PairedUsersList.vue'
import PairedUserForm from '@/components/PairedUserForm.vue'

export default {
  name: 'PairedUsersView',
  components: {
    PairedUsersList,
    PairedUserForm
  },
  setup() {
    const store = useStore()
    const showForm = ref(false)
    const pairedUsersList = ref(null)

    const isAdmin = computed(() => {
      return store.getters['auth/isAdmin']
    })

    const handlePairingCreated = () => {
      showForm.value = false
      // Refresh the list
      if (pairedUsersList.value) {
        pairedUsersList.value.fetchPairedUsers()
      }
    }

    return {
      showForm,
      isAdmin,
      pairedUsersList,
      handlePairingCreated
    }
  }
}
</script>

<style scoped>
.paired-users-view {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h1 {
  color: #2c3e50;
  margin: 0;
}

.btn {
  padding: 10px 20px;
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

.mt-4 {
  margin-top: 1.5rem;
}
</style> 