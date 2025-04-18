const express = require('express')
const router = express.Router()
const { body, validationResult } = require('express-validator')
const Investment = require('../models/Investment')
const User = require('../models/User')
const Referral = require('../models/Referral')
const { protect, authorize } = require('../middleware/auth')

// Validation middleware for investment creation
const validateInvestment = [
  body('amount')
    .isFloat({ min: 100 })
    .withMessage('Minimum investment amount is $100'),
  body('duration')
    .isIn([4, 8, 16, 30])
    .withMessage('Duration must be either 4, 8, 16, or 30 days')
]

// Get user's investments
router.get('/', protect, async (req, res) => {
  try {
    const investments = await Investment.find({ user: req.user.id })
      .sort('-createdAt')
    res.json(investments)
  } catch (error) {
    console.error('Error fetching investments:', error)
    res.status(500).json({ message: 'Error fetching investments' })
  }
})

// Get investment statistics
router.get('/stats', protect, async (req, res) => {
  try {
    const stats = await Investment.aggregate([
      { $match: { user: req.user._id, status: 'active' } },
      {
        $group: {
          _id: null,
          totalInvested: { $sum: '$amount' },
          totalEarnings: { $sum: '$expectedReturn' },
          count: { $sum: 1 }
        }
      }
    ])

    res.json(stats[0] || { totalInvested: 0, totalEarnings: 0, count: 0 })
  } catch (error) {
    console.error('Error fetching investment stats:', error)
    res.status(500).json({ message: 'Error fetching investment statistics' })
  }
})

// Create new investment
router.post('/', protect, validateInvestment, async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    const { amount, duration } = req.body

    // Create new investment
    const investment = new Investment({
      user: req.user.id,
      amount: Number(amount),
      duration: Number(duration),
      status: 'pending'
    })

    // Save investment - this will trigger the pre-save hook
    await investment.save()
    
    res.status(201).json(investment)
  } catch (error) {
    console.error('Error creating investment:', error)
    res.status(500).json({ message: 'Error creating investment' })
  }
})

// Admin routes
router.get('/admin', protect, authorize('admin'), async (req, res) => {
  try {
    const investments = await Investment.find()
      .populate('user', 'username email')
      .sort('-createdAt')
    res.json(investments)
  } catch (error) {
    console.error('Error fetching all investments:', error)
    res.status(500).json({ message: 'Error fetching investments' })
  }
})

module.exports = router 