import axios from 'axios'

export default {
  namespaced: true,
  state: {
    investments: [],
    currentInvestment: null,
    investmentStats: {
      totalInvested: 0,
      totalEarnings: 0,
      activeInvestments: 0
    },
    loading: false,
    error: null
  },
  mutations: {
    SET_INVESTMENTS(state, investments) {
      state.investments = investments
    },
    SET_CURRENT_INVESTMENT(state, investment) {
      state.currentInvestment = investment
    },
    SET_INVESTMENT_STATS(state, stats) {
      state.investmentStats = stats
    },
    ADD_INVESTMENT(state, investment) {
      state.investments.push(investment)
    },
    UPDATE_INVESTMENT(state, updatedInvestment) {
      const index = state.investments.findIndex(inv => inv._id === updatedInvestment._id)
      if (index !== -1) {
        state.investments.splice(index, 1, updatedInvestment)
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    async fetchInvestments({ commit }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await axios.get('/api/investments/my-investments')
        commit('SET_INVESTMENTS', response.data.data || [])
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch investments')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async createInvestment({ commit }, investmentData) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await axios.post('/api/investments', investmentData)
        commit('ADD_INVESTMENT', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to create investment')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async updateInvestment({ commit }, { id, data }) {
      try {
        const response = await axios.put(`/api/investments/${id}`, data)
        commit('UPDATE_INVESTMENT', response.data)
        return response.data
      } catch (error) {
        throw error
      }
    },
    async fetchInvestmentStats({ commit }) {
      try {
        const response = await axios.get('/api/investments/stats')
        commit('SET_INVESTMENT_STATS', response.data)
        return response.data
      } catch (error) {
        throw error
      }
    }
  },
  getters: {
    allInvestments: state => state.investments,
    currentInvestment: state => state.currentInvestment,
    investmentStats: state => state.investmentStats,
    activeInvestments: state => state.investments.filter(inv => inv.status === 'active'),
    completedInvestments: state => state.investments.filter(inv => inv.status === 'completed'),
    loading: state => state.loading,
    error: state => state.error
  }
} 