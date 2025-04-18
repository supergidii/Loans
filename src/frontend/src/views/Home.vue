<template>
  <div class="home">
    <div class="container">
      <h1 class="text-center mt-4">Welcome to Referral Investment System</h1>
      <div class="row mt-4">
        <div class="col-md-4">
          <div class="card">
            <h3>Start Investing</h3>
            <p>Begin your investment journey with our secure platform.</p>
            <router-link to="/investments" class="btn btn-primary">View Investments</router-link>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <h3>Refer & Earn</h3>
            <p>Invite friends and earn commissions on their investments.</p>
            <router-link to="/referrals" class="btn btn-primary">View Referrals</router-link>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <h3>Track Progress</h3>
            <p>Monitor your investments and earnings in real-time.</p>
            <router-link to="/dashboard" class="btn btn-primary">Go to Dashboard</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  padding: 20px 0;
}

.card {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.card h3 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.card p {
  margin-bottom: 20px;
  color: #666;
}

.btn {
  margin-top: auto;
}
</style> 