import axios from 'axios'

export default {
  namespaced: true,
  state: {
    referrals: [],
    referralStats: {
      totalReferrals: 0,
      totalEarnings: 0,
      activeReferrals: 0
    },
    referralCode: null
  },
  mutations: {
    SET_REFERRALS(state, referrals) {
      state.referrals = referrals
    },
    SET_REFERRAL_STATS(state, stats) {
      state.referralStats = stats
    },
    SET_REFERRAL_CODE(state, code) {
      state.referralCode = code
    },
    ADD_REFERRAL(state, referral) {
      state.referrals.push(referral)
    },
    UPDATE_REFERRAL(state, updatedReferral) {
      const index = state.referrals.findIndex(ref => ref._id === updatedReferral._id)
      if (index !== -1) {
        state.referrals.splice(index, 1, updatedReferral)
      }
    }
  },
  actions: {
    async fetchReferrals({ commit }) {
      try {
        const response = await axios.get('/api/referrals')
        commit('SET_REFERRALS', response.data.referrals)
        commit('SET_REFERRAL_STATS', response.data.stats)
        return response.data
      } catch (error) {
        throw error
      }
    },
    async generateReferralCode({ commit }) {
      try {
        const response = await axios.post('/api/referrals/generate-code')
        commit('SET_REFERRAL_CODE', response.data.code)
        return response.data.code
      } catch (error) {
        throw error
      }
    },
    async fetchReferralStats({ commit }) {
      try {
        const response = await axios.get('/api/referrals/stats')
        commit('SET_REFERRAL_STATS', response.data)
        return response.data
      } catch (error) {
        throw error
      }
    },
    async updateReferral({ commit }, { id, data }) {
      try {
        const response = await axios.put(`/api/referrals/${id}`, data)
        commit('UPDATE_REFERRAL', response.data)
        return response.data
      } catch (error) {
        throw error
      }
    }
  },
  getters: {
    allReferrals: state => state.referrals,
    referralStats: state => state.referralStats,
    referralCode: state => state.referralCode,
    activeReferrals: state => state.referrals.filter(ref => ref.status === 'active'),
    completedReferrals: state => state.referrals.filter(ref => ref.status === 'completed')
  }
} 