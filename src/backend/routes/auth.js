const express = require('express')
const router = express.Router()
const { body, validationResult } = require('express-validator')
const jwt = require('jsonwebtoken')
const User = require('../models/User')
const { protect } = require('../middleware/auth')
const { register, login, getMe } = require('../controllers/auth')

// Validation middleware
const registerValidation = [
  body('firstName').trim().notEmpty().withMessage('First name is required'),
  body('lastName').trim().notEmpty().withMessage('Last name is required'),
  body('username').trim().notEmpty().withMessage('Username is required'),
  body('email').isEmail().withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long'),
  body('referralCode').optional()
]

const loginValidation = [
  body('email').isEmail().withMessage('Please provide a valid email'),
  body('password').notEmpty().withMessage('Password is required')
]

// Register user
router.post('/register', registerValidation, async (req, res) => {
  try {
    console.log('Registration request received:', req.body)
    
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      console.log('Validation errors:', errors.array())
      return res.status(400).json({
        success: false,
        message: errors.array()[0].msg
      })
    }

    const { firstName, lastName, email, password, referralCode, username } = req.body
    console.log('Processing registration for:', { firstName, lastName, email, username, referralCode })

    // Check if user exists
    const userExists = await User.findOne({ $or: [{ email }, { username }] })
    if (userExists) {
      console.log('User already exists:', userExists.email === email ? 'email' : 'username')
      return res.status(400).json({
        success: false,
        message: userExists.email === email 
          ? 'User with this email already exists' 
          : 'Username is already taken'
      })
    }

    // Find referrer if referral code provided
    let referredBy = null
    if (referralCode) {
      console.log('Looking up referrer with code:', referralCode)
      const referrer = await User.findOne({ referralCode })
      if (referrer) {
        referredBy = referrer._id
        console.log('Referrer found:', referrer._id)
      }
    }

    // Create user with all required fields
    console.log('Creating new user with username:', username)
    const user = await User.create({
      firstName,
      lastName,
      email,
      username,
      password,
      referredBy,
      referralCode: Math.random().toString(36).substring(2, 8).toUpperCase() // Generate a unique referral code
    })
    console.log('User created successfully:', user._id)

    // Generate JWT token
    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRE }
    )

    // Remove password from response
    user.password = undefined

    console.log('Registration successful, sending response')
    res.status(201).json({
      success: true,
      token,
      user
    })
  } catch (error) {
    console.error('Registration error:', error)
    res.status(500).json({
      success: false,
      message: error.message || 'Error registering user'
    })
  }
})

// Login user
router.post('/login', loginValidation, async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: errors.array()[0].msg
      })
    }

    const { email, password } = req.body

    // Check if user exists
    const user = await User.findOne({ email }).select('+password')
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      })
    }

    // Check password
    const isMatch = await user.matchPassword(password)
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      })
    }

    // Generate JWT token
    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRE }
    )

    // Update last login
    user.lastLogin = Date.now()
    await user.save()

    // Remove password from response
    user.password = undefined

    res.json({
      success: true,
      token,
      user
    })
  } catch (error) {
    console.error('Login error:', error)
    res.status(500).json({
      success: false,
      message: 'Error logging in'
    })
  }
})

// Get current user
router.get('/me', protect, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password')
    res.json(user)
  } catch (error) {
    console.error('Get user error:', error)
    res.status(500).json({
      success: false,
      message: 'Error fetching user data'
    })
  }
})

// Request password reset
router.post('/forgot-password', [
  body('email').isEmail().withMessage('Please provide a valid email')
], async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    const user = await User.findOne({ email: req.body.email })
    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      })
    }

    // Generate reset token
    const resetToken = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    )

    user.resetPasswordToken = resetToken
    user.resetPasswordExpire = Date.now() + 3600000 // 1 hour
    await user.save()

    // TODO: Send email with reset link

    res.json({
      success: true,
      message: 'Password reset email sent'
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Reset password
router.post('/reset-password/:token', [
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
], async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    const user = await User.findOne({
      resetPasswordToken: req.params.token,
      resetPasswordExpire: { $gt: Date.now() }
    })

    if (!user) {
      return res.status(400).json({
        success: false,
        error: 'Invalid or expired reset token'
      })
    }

    user.password = req.body.password
    user.resetPasswordToken = undefined
    user.resetPasswordExpire = undefined
    await user.save()

    res.json({
      success: true,
      message: 'Password reset successful'
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

module.exports = router 