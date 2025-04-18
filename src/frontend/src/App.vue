<template>
  <div id="app">
    <nav v-if="!isLoginPage" class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/">Referral Investment System</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/investments">Investments</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/referrals">Referrals</router-link>
            </li>
          </ul>
          <div class="navbar-nav">
            <template v-if="isAuthenticated">
              <div class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                  {{ user.name }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
                  <li><router-link class="dropdown-item" to="/settings">Settings</router-link></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item" href="#" @click="logout">Logout</a></li>
                </ul>
              </div>
            </template>
            <template v-else>
              <router-link class="nav-link" to="/login">Login</router-link>
              <router-link class="nav-link" to="/register">Register</router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <main class="container-fluid py-4">
      <router-view></router-view>
    </main>

    <footer class="footer mt-auto py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">© 2024 Referral Investment System. All rights reserved.</span>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const store = useStore()
    const route = useRoute()

    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    const user = computed(() => store.getters['auth/user'])
    const isLoginPage = computed(() => route.path === '/login' || route.path === '/register')

    const logout = async () => {
      await store.dispatch('auth/logout')
    }

    return {
      isAuthenticated,
      user,
      isLoginPage,
      logout
    }
  }
}
</script>

<style lang="scss">
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

.footer {
  margin-top: auto;
}
</style> 