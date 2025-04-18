<template>
  <div class="login">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card mt-5">
            <h2 class="text-center mb-4">Login</h2>
            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label for="email">Email</label>
                <input
                  type="email"
                  id="email"
                  v-model="email"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group">
                <label for="password">Password</label>
                <input
                  type="password"
                  id="password"
                  v-model="password"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group">
                <button type="submit" class="btn btn-primary w-100">Login</button>
              </div>
              <div class="text-center mt-3">
                <router-link to="/forgot-password">Forgot Password?</router-link>
              </div>
              <div class="text-center mt-3">
                Don't have an account?
                <router-link to="/register">Register</router-link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    const email = ref('')
    const password = ref('')

    const handleLogin = async () => {
      try {
        await store.dispatch('auth/login', {
          email: email.value,
          password: password.value
        })
        router.push('/dashboard')
      } catch (error) {
        console.error('Login failed:', error)
      }
    }

    return {
      email,
      password,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
}

.card {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}
</style> 