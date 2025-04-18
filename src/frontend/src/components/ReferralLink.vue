<template>
  <div class="referral-link-container">
    <h2>Your Referral Link</h2>
    
    <div v-if="loading" class="loading">
      Loading referral code...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else class="referral-content">
      <div class="referral-code">
        <input 
          type="text" 
          :value="referralLink" 
          readonly 
          ref="referralInput"
          class="referral-input"
        />
        <button 
          @click="copyToClipboard" 
          class="copy-button"
          :class="{ 'copied': copied }"
        >
          {{ copied ? 'Copied!' : 'Copy' }}
        </button>
      </div>
      
      <div class="referral-stats" v-if="referralStats">
        <div class="stat-card">
          <h4>Total Referrals</h4>
          <p>{{ referralStats.totalReferrals }}</p>
        </div>
        <div class="stat-card">
          <h4>Active Referrals</h4>
          <p>{{ referralStats.activeReferrals }}</p>
        </div>
        <div class="stat-card">
          <h4>Total Earnings</h4>
          <p>${{ referralStats.totalEarnings.toFixed(2) }}</p>
        </div>
      </div>
      
      <div class="share-buttons">
        <button @click="shareOnWhatsApp" class="share-button whatsapp">
          Share on WhatsApp
        </button>
        <button @click="shareOnTelegram" class="share-button telegram">
          Share on Telegram
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ReferralLink',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const error = ref(null)
    const copied = ref(false)
    const referralInput = ref(null)

    const referralCode = computed(() => store.state.referrals.referralCode)
    const referralStats = computed(() => store.state.referrals.referralStats)
    
    const referralLink = computed(() => {
      if (!referralCode.value) return ''
      const baseUrl = window.location.origin
      return `${baseUrl}/register?ref=${referralCode.value}`
    })

    const copyToClipboard = async () => {
      try {
        await navigator.clipboard.writeText(referralLink.value)
        copied.value = true
        setTimeout(() => {
          copied.value = false
        }, 2000)
      } catch (err) {
        console.error('Failed to copy:', err)
        error.value = 'Failed to copy to clipboard'
      }
    }

    const shareOnWhatsApp = () => {
      const text = `Join me on our investment platform! Use my referral link: ${referralLink.value}`
      const url = `https://wa.me/?text=${encodeURIComponent(text)}`
      window.open(url, '_blank')
    }

    const shareOnTelegram = () => {
      const text = `Join me on our investment platform! Use my referral link: ${referralLink.value}`
      const url = `https://t.me/share/url?url=${encodeURIComponent(referralLink.value)}&text=${encodeURIComponent(text)}`
      window.open(url, '_blank')
    }

    const fetchReferralData = async () => {
      try {
        loading.value = true
        error.value = null
        
        if (!referralCode.value) {
          await store.dispatch('referrals/generateReferralCode')
        }
        await store.dispatch('referrals/fetchReferralStats')
      } catch (err) {
        console.error('Error fetching referral data:', err)
        error.value = 'Failed to load referral data'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchReferralData()
    })

    return {
      loading,
      error,
      copied,
      referralInput,
      referralLink,
      referralStats,
      copyToClipboard,
      shareOnWhatsApp,
      shareOnTelegram
    }
  }
}
</script>

<style scoped>
.referral-link-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: #dc3545;
}

.referral-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.referral-code {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.referral-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background: #f8f9fa;
}

.copy-button {
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.copy-button:hover {
  background: #45a049;
}

.copy-button.copied {
  background: #2196F3;
}

.referral-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.stat-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
}

.stat-card h4 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 0.9rem;
}

.stat-card p {
  margin: 0;
  font-size: 1.5em;
  font-weight: 600;
  color: #2c3e50;
}

.share-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.share-button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: opacity 0.2s;
}

.share-button:hover {
  opacity: 0.9;
}

.whatsapp {
  background: #25D366;
}

.telegram {
  background: #0088cc;
}
</style> 