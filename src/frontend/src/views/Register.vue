<template>
  <div class="register">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card mt-5">
            <h2 class="text-center mb-4">Register</h2>
            <div v-if="error" class="alert alert-danger">
              <strong>Error:</strong> {{ error }}
            </div>
            <form @submit.prevent="handleRegister">
              <div class="form-group">
                <label for="firstName">First Name</label>
                <input
                  type="text"
                  id="firstName"
                  v-model="firstName"
                  class="form-control"
                  :class="{ 'is-invalid': firstNameError }"
                  @blur="validateFirstName"
                  required
                />
                <div class="invalid-feedback" v-if="firstNameError">
                  {{ firstNameError }}
                </div>
              </div>

              <div class="form-group">
                <label for="username">Username</label>
                <input
                  type="text"
                  id="username"
                  v-model="username"
                  class="form-control"
                  :class="{ 'is-invalid': usernameError }"
                  @blur="validateUsername"
                  required
                />
                <div class="invalid-feedback" v-if="usernameError">
                  {{ usernameError }}
                </div>
              </div>

              <div class="form-group">
                <label for="lastName">Last Name</label>
                <input
                  type="text"
                  id="lastName"
                  v-model="lastName"
                  class="form-control"
                  :class="{ 'is-invalid': lastNameError }"
                  @blur="validateLastName"
                  required
                />
                <div class="invalid-feedback" v-if="lastNameError">
                  {{ lastNameError }}
                </div>
              </div>

              <div class="form-group">
                <label for="email">Email</label>
                <input
                  type="email"
                  id="email"
                  v-model="email"
                  class="form-control"
                  :class="{ 'is-invalid': emailError }"
                  @blur="validateEmail"
                  required
                />
                <div class="invalid-feedback" v-if="emailError">
                  {{ emailError }}
                </div>
              </div>

              <div class="form-group">
                <label for="password">Password</label>
                <input
                  type="password"
                  id="password"
                  v-model="password"
                  class="form-control"
                  :class="{ 'is-invalid': passwordError }"
                  @blur="validatePassword"
                  required
                />
                <div class="invalid-feedback" v-if="passwordError">
                  {{ passwordError }}
                </div>
                <small class="form-text text-muted">
                  Password must be at least 6 characters long and contain at least one number
                </small>
              </div>

              <div class="form-group">
                <label for="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  v-model="confirmPassword"
                  class="form-control"
                  :class="{ 'is-invalid': confirmPasswordError }"
                  @blur="validateConfirmPassword"
                  required
                />
                <div class="invalid-feedback" v-if="confirmPasswordError">
                  {{ confirmPasswordError }}
                </div>
              </div>

              <div class="form-group">
                <label for="referralCode">Referral Code (Optional)</label>
                <input
                  type="text"
                  id="referralCode"
                  v-model="referralCode"
                  class="form-control"
                  :class="{ 'is-invalid': referralCodeError }"
                  @blur="validateReferralCode"
                />
                <div class="invalid-feedback" v-if="referralCodeError">
                  {{ referralCodeError }}
                </div>
              </div>

              <div class="form-group">
                <button 
                  type="submit" 
                  class="btn btn-primary w-100" 
                  :disabled="loading || !isFormValid"
                >
                  {{ loading ? 'Registering...' : 'Register' }}
                </button>
              </div>

              <div class="text-center mt-3">
                Already have an account?
                <router-link to="/login">Login</router-link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // Form fields
    const firstName = ref('')
    const lastName = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const referralCode = ref('')
    const username = ref('')
    
    // Error states
    const loading = ref(false)
    const error = ref('')
    const firstNameError = ref('')
    const lastNameError = ref('')
    const emailError = ref('')
    const passwordError = ref('')
    const confirmPasswordError = ref('')
    const referralCodeError = ref('')
    const usernameError = ref('')

    // Validation functions
    const validateFirstName = () => {
      if (!firstName.value) {
        firstNameError.value = 'First name is required'
        return false
      }
      if (firstName.value.length < 2) {
        firstNameError.value = 'First name must be at least 2 characters'
        return false
      }
      if (!/^[a-zA-Z\s]*$/.test(firstName.value)) {
        firstNameError.value = 'First name can only contain letters and spaces'
        return false
      }
      firstNameError.value = ''
      return true
    }

    const validateLastName = () => {
      if (!lastName.value) {
        lastNameError.value = 'Last name is required'
        return false
      }
      if (lastName.value.length < 2) {
        lastNameError.value = 'Last name must be at least 2 characters'
        return false
      }
      if (!/^[a-zA-Z\s]*$/.test(lastName.value)) {
        lastNameError.value = 'Last name can only contain letters and spaces'
        return false
      }
      lastNameError.value = ''
      return true
    }

    const validateEmail = () => {
      if (!email.value) {
        emailError.value = 'Email is required'
        return false
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email.value)) {
        emailError.value = 'Please enter a valid email address'
        return false
      }
      emailError.value = ''
      return true
    }

    const validatePassword = () => {
      if (!password.value) {
        passwordError.value = 'Password is required'
        return false
      }
      if (password.value.length < 6) {
        passwordError.value = 'Password must be at least 6 characters'
        return false
      }
      if (!/\d/.test(password.value)) {
        passwordError.value = 'Password must contain at least one number'
        return false
      }
      passwordError.value = ''
      return true
    }

    const validateConfirmPassword = () => {
      if (!confirmPassword.value) {
        confirmPasswordError.value = 'Please confirm your password'
        return false
      }
      if (confirmPassword.value !== password.value) {
        confirmPasswordError.value = 'Passwords do not match'
        return false
      }
      confirmPasswordError.value = ''
      return true
    }

    const validateReferralCode = () => {
      if (referralCode.value && !/^[A-Z0-9]{6}$/.test(referralCode.value)) {
        referralCodeError.value = 'Referral code must be 6 characters (letters and numbers)'
        return false
      }
      referralCodeError.value = ''
      return true
    }

    const validateUsername = () => {
      if (!username.value) {
        usernameError.value = 'Username is required'
        return false
      }
      if (username.value.length < 3) {
        usernameError.value = 'Username must be at least 3 characters'
        return false
      }
      if (!/^[a-zA-Z0-9_]+$/.test(username.value)) {
        usernameError.value = 'Username can only contain letters, numbers, and underscores'
        return false
      }
      usernameError.value = ''
      return true
    }

    // Form validation
    const isFormValid = computed(() => {
      return firstName.value &&
        lastName.value &&
        email.value &&
        password.value &&
        confirmPassword.value &&
        username.value &&
        !firstNameError.value &&
        !lastNameError.value &&
        !emailError.value &&
        !passwordError.value &&
        !confirmPasswordError.value &&
        !referralCodeError.value &&
        !usernameError.value
    })

    const handleRegister = async () => {
      error.value = ''
      
      // Validate all fields
      const isFirstNameValid = validateFirstName()
      const isLastNameValid = validateLastName()
      const isEmailValid = validateEmail()
      const isPasswordValid = validatePassword()
      const isConfirmPasswordValid = validateConfirmPassword()
      const isReferralCodeValid = validateReferralCode()
      const isUsernameValid = validateUsername()

      if (!isFirstNameValid || !isLastNameValid || !isEmailValid || 
          !isPasswordValid || !isConfirmPasswordValid || !isReferralCodeValid ||
          !isUsernameValid) {
        return
      }

      loading.value = true
      try {
        console.log('Attempting registration with:', {
          firstName: firstName.value,
          lastName: lastName.value,
          email: email.value,
          username: username.value,
          referralCode: referralCode.value
        })

        await store.dispatch('auth/register', {
          firstName: firstName.value,
          lastName: lastName.value,
          email: email.value,
          password: password.value,
          username: username.value,
          referralCode: referralCode.value
        })
        
        console.log('Registration successful, redirecting to dashboard')
        router.push('/dashboard')
      } catch (err) {
        console.error('Registration error:', {
          message: err.message,
          response: err.response?.data,
          status: err.response?.status
        })
        error.value = err.response?.data?.message || 'Registration failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      firstName,
      lastName,
      email,
      password,
      confirmPassword,
      referralCode,
      username,
      loading,
      error,
      firstNameError,
      lastNameError,
      emailError,
      passwordError,
      confirmPasswordError,
      referralCodeError,
      usernameError,
      validateFirstName,
      validateLastName,
      validateEmail,
      validatePassword,
      validateConfirmPassword,
      validateReferralCode,
      validateUsername,
      isFormValid,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
}

.card {
  padding: 2rem;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
}

.invalid-feedback {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
}

.form-text {
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.btn-primary {
  padding: 0.75rem;
  font-weight: 500;
}

.btn-primary:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}
</style> 