<template>
  <div class="admin-dashboard">
    <div class="admin-header">
      <h1>Admin Dashboard</h1>
      <nav class="admin-nav">
        <router-link to="/admin/users" class="nav-link">Users</router-link>
        <router-link to="/admin/investments" class="nav-link">Investments</router-link>
        <router-link to="/admin/referrals" class="nav-link">Referrals</router-link>
        <router-link to="/admin/paired-users" class="nav-link">Paired Users</router-link>
        <router-link to="/admin/settings" class="nav-link">Settings</router-link>
      </nav>
    </div>

    <div class="admin-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard'
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.admin-header {
  background-color: white;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.admin-nav {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.nav-link {
  text-decoration: none;
  color: #666;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-link:hover {
  background-color: #f0f0f0;
  color: #2c3e50;
}

.nav-link.router-link-active {
  background-color: #4CAF50;
  color: white;
}

.admin-content {
  padding: 20px;
}
</style> 