const jwt = require('jsonwebtoken')
const User = require('../models/User')

const protect = async (req, res, next) => {
  try {
    let token

    // Check if token exists in headers
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1]
      console.log('Token found in headers:', token.substring(0, 10) + '...')
    } else {
      console.log('No authorization header found or not Bearer token')
    }

    if (!token) {
      console.log('No token provided')
      return res.status(401).json({
        success: false,
        message: 'Not authorized to access this route'
      })
    }

    try {
      // Verify token
      console.log('Verifying token with secret:', process.env.JWT_SECRET ? 'Secret exists' : 'No secret found')
      const decoded = jwt.verify(token, process.env.JWT_SECRET)
      console.log('Token decoded successfully, user ID:', decoded.id)

      // Get user from token
      req.user = await User.findById(decoded.id).select('-password')
      if (!req.user) {
        console.log('User not found for ID:', decoded.id)
        return res.status(401).json({
          success: false,
          message: 'User not found'
        })
      }

      console.log('User authenticated successfully:', req.user._id)
      next()
    } catch (error) {
      console.error('Token verification error:', error.message)
      return res.status(401).json({
        success: false,
        message: 'Not authorized to access this route'
      })
    }
  } catch (error) {
    console.error('Auth middleware error:', error)
    res.status(500).json({
      success: false,
      message: 'Server error'
    })
  }
}

const authorize = (...roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        error: `User role ${req.user.role} is not authorized to access this route`
      })
    }
    next()
  }
}

const verifyEmail = async (req, res, next) => {
  try {
    if (!req.user.isVerified) {
      return res.status(403).json({
        success: false,
        error: 'Please verify your email address to access this route'
      })
    }
    next()
  } catch (error) {
    next(error)
  }
}

module.exports = { protect, authorize, verifyEmail } 