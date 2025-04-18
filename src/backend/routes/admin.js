const express = require('express')
const router = express.Router()
const { body, validationResult } = require('express-validator')
const User = require('../models/User')
const Investment = require('../models/Investment')
const Referral = require('../models/Referral')
const { protect, authorize } = require('../middleware/auth')

// Apply admin middleware to all routes
router.use(protect, authorize('admin'))

// Get dashboard stats
router.get('/dashboard', async (req, res) => {
  try {
    const [
      totalUsers,
      totalInvestments,
      totalReferrals,
      activeInvestments,
      recentUsers,
      recentInvestments
    ] = await Promise.all([
      User.countDocuments(),
      Investment.countDocuments(),
      Referral.countDocuments(),
      Investment.countDocuments({ status: 'active' }),
      User.find().sort('-createdAt').limit(5),
      Investment.find()
        .populate('user', 'name email')
        .sort('-createdAt')
        .limit(5)
    ])

    const totalRevenue = await Investment.aggregate([
      {
        $match: { status: 'completed' }
      },
      {
        $group: {
          _id: null,
          total: { $sum: '$amount' }
        }
      }
    ])

    res.json({
      success: true,
      stats: {
        totalUsers,
        totalInvestments,
        totalReferrals,
        activeInvestments,
        totalRevenue: totalRevenue[0]?.total || 0
      },
      recentUsers,
      recentInvestments
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Get all users
router.get('/users', async (req, res) => {
  try {
    const users = await User.find()
      .select('-password')
      .sort('-createdAt')

    res.json({
      success: true,
      count: users.length,
      users
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Update user
router.patch('/users/:id', [
  body('role').optional().isIn(['user', 'admin']),
  body('isVerified').optional().isBoolean(),
  body('wallet.balance').optional().isFloat({ min: 0 })
], async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    const user = await User.findById(req.params.id)
    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      })
    }

    // Update allowed fields
    const allowedUpdates = ['role', 'isVerified', 'wallet']
    Object.keys(req.body).forEach(key => {
      if (allowedUpdates.includes(key)) {
        if (key === 'wallet') {
          user.wallet = { ...user.wallet, ...req.body.wallet }
        } else {
          user[key] = req.body[key]
        }
      }
    })

    await user.save()

    res.json({
      success: true,
      user
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Get system settings
router.get('/settings', async (req, res) => {
  try {
    // TODO: Implement settings model and retrieval
    res.json({
      success: true,
      settings: {
        investmentTypes: {
          standard: { rate: 5, minAmount: 100 },
          premium: { rate: 10, minAmount: 1000 },
          vip: { rate: 15, minAmount: 5000 }
        },
        referralCommission: 2,
        maintenanceMode: false
      }
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Update system settings
router.patch('/settings', [
  body('investmentTypes.*.rate').optional().isFloat({ min: 0 }),
  body('investmentTypes.*.minAmount').optional().isFloat({ min: 0 }),
  body('referralCommission').optional().isFloat({ min: 0, max: 100 }),
  body('maintenanceMode').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    // TODO: Implement settings model and update
    res.json({
      success: true,
      message: 'Settings updated successfully'
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Get system logs
router.get('/logs', async (req, res) => {
  try {
    // TODO: Implement logging system
    res.json({
      success: true,
      logs: []
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

module.exports = router 