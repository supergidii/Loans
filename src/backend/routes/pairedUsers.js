const express = require('express')
const router = express.Router()
const { body, validationResult } = require('express-validator')
const { protect, authorize } = require('../middleware/auth')
const PairedUser = require('../models/PairedUser')
const User = require('../models/User')

// Get all paired users (admin only)
router.get('/', protect, authorize('admin'), async (req, res) => {
  try {
    const pairedUsers = await PairedUser.find()
      .populate('user1', 'username firstName lastName email')
      .populate('user2', 'username firstName lastName email')
      .populate('createdBy', 'username')
      .populate('investment')
      .populate('referral')
      .sort('-createdAt')

    res.json({
      success: true,
      count: pairedUsers.length,
      data: pairedUsers
    })
  } catch (error) {
    console.error('Error fetching paired users:', error)
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Get paired users for a specific user
router.get('/my-pairings', protect, async (req, res) => {
  try {
    const pairedUsers = await PairedUser.find({
      $or: [{ user1: req.user.id }, { user2: req.user.id }]
    })
      .populate('user1', 'username firstName lastName email')
      .populate('user2', 'username firstName lastName email')
      .populate('createdBy', 'username')
      .populate('investment')
      .populate('referral')
      .sort('-createdAt')

    res.json({
      success: true,
      count: pairedUsers.length,
      data: pairedUsers
    })
  } catch (error) {
    console.error('Error fetching user pairings:', error)
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Create a new paired user relationship
router.post('/', [
  protect,
  authorize('admin'),
  body('user1').notEmpty().withMessage('User1 ID is required'),
  body('user2').notEmpty().withMessage('User2 ID is required'),
  body('pairingType').isIn(['investment', 'referral', 'manual']).withMessage('Invalid pairing type'),
  body('notes').optional().isString()
], async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    // Check if users exist
    const user1 = await User.findById(req.body.user1)
    const user2 = await User.findById(req.body.user2)

    if (!user1 || !user2) {
      return res.status(404).json({
        success: false,
        error: 'One or both users not found'
      })
    }

    // Check for existing pairing
    const existingPairing = await PairedUser.findOne({
      $or: [
        { user1: req.body.user1, user2: req.body.user2 },
        { user1: req.body.user2, user2: req.body.user1 }
      ],
      status: { $in: ['pending', 'active'] }
    })

    if (existingPairing) {
      return res.status(400).json({
        success: false,
        error: 'Users are already paired'
      })
    }

    // Create new pairing
    const pairedUser = await PairedUser.create({
      user1: req.body.user1,
      user2: req.body.user2,
      pairingType: req.body.pairingType,
      notes: req.body.notes,
      createdBy: req.user.id,
      investment: req.body.investment,
      referral: req.body.referral
    })

    res.status(201).json({
      success: true,
      data: pairedUser
    })
  } catch (error) {
    console.error('Error creating paired user:', error)
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Update paired user status
router.patch('/:id', [
  protect,
  authorize('admin'),
  body('status').isIn(['pending', 'active', 'completed', 'cancelled']).withMessage('Invalid status'),
  body('notes').optional().isString()
], async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    const pairedUser = await PairedUser.findById(req.params.id)
    if (!pairedUser) {
      return res.status(404).json({
        success: false,
        error: 'Paired user relationship not found'
      })
    }

    // Update fields
    pairedUser.status = req.body.status
    if (req.body.notes) pairedUser.notes = req.body.notes
    
    // Set end date if status is completed or cancelled
    if (['completed', 'cancelled'].includes(req.body.status)) {
      pairedUser.endDate = Date.now()
    }

    await pairedUser.save()

    res.json({
      success: true,
      data: pairedUser
    })
  } catch (error) {
    console.error('Error updating paired user:', error)
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Delete paired user relationship (admin only)
router.delete('/:id', protect, authorize('admin'), async (req, res) => {
  try {
    const pairedUser = await PairedUser.findById(req.params.id)
    if (!pairedUser) {
      return res.status(404).json({
        success: false,
        error: 'Paired user relationship not found'
      })
    }

    await pairedUser.remove()

    res.json({
      success: true,
      data: {}
    })
  } catch (error) {
    console.error('Error deleting paired user:', error)
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

module.exports = router 