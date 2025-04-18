<template>
  <div class="dashboard">
    <div class="container">
      <div class="row">
        <div class="col-md-4">
          <div class="card mb-4">
            <div class="card-body">
              <h2>Create Investment</h2>
              <InvestmentForm @investment-created="handleInvestmentCreated" />
            </div>
          </div>
        </div>
        <div class="col-md-8">
          <div class="card">
            <div class="card-body">
              <InvestmentList ref="investmentList" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import InvestmentForm from '../components/InvestmentForm.vue'
import InvestmentList from '../components/InvestmentList.vue'

export default {
  name: 'Dashboard',
  components: {
    InvestmentForm,
    InvestmentList
  },
  methods: {
    handleInvestmentCreated() {
      // Refresh the investment list when a new investment is created
      this.$refs.investmentList.fetchInvestments()
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card {
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 8px;
}

.card-body {
  padding: 1.5rem;
}

h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}
</style> 