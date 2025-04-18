const express = require('express')
const router = express.Router()
const { body, validationResult } = require('express-validator')
const Referral = require('../models/Referral')
const User = require('../models/User')
const { protect, authorize } = require('../middleware/auth')

// Get all referrals (admin only)
router.get('/', protect, authorize('admin'), async (req, res) => {
  try {
    const referrals = await Referral.find()
      .populate('referrer', 'name email')
      .populate('referred', 'name email')
      .populate('investment', 'amount type status')
      .sort('-createdAt')

    res.json({
      success: true,
      count: referrals.length,
      referrals
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Get user's referrals
router.get('/my-referrals', protect, async (req, res) => {
  try {
    const referrals = await Referral.find({ referrer: req.user.id })
      .populate('referred', 'name email')
      .populate('investment', 'amount type status')
      .sort('-createdAt')

    res.json({
      success: true,
      count: referrals.length,
      referrals
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Get referral stats
router.get('/stats', protect, async (req, res) => {
  try {
    const stats = await Referral.aggregate([
      {
        $match: {
          referrer: req.user._id,
          status: { $in: ['active', 'completed'] }
        }
      },
      {
        $group: {
          _id: null,
          totalReferrals: { $sum: 1 },
          totalEarnings: { $sum: '$commission' },
          activeReferrals: {
            $sum: { $cond: [{ $eq: ['$status', 'active'] }, 1, 0] }
          }
        }
      }
    ])

    res.json({
      success: true,
      stats: stats[0] || {
        totalReferrals: 0,
        totalEarnings: 0,
        activeReferrals: 0
      }
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Generate referral code
router.post('/generate-code', protect, async (req, res) => {
  try {
    const user = await User.findById(req.user.id)
    
    if (!user.referralCode) {
      user.referralCode = Math.random().toString(36).substring(2, 8).toUpperCase()
      await user.save()
    }

    res.json({
      success: true,
      code: user.referralCode
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Get single referral
router.get('/:id', protect, async (req, res) => {
  try {
    const referral = await Referral.findById(req.params.id)
      .populate('referrer', 'name email')
      .populate('referred', 'name email')
      .populate('investment', 'amount type status')

    if (!referral) {
      return res.status(404).json({
        success: false,
        error: 'Referral not found'
      })
    }

    // Check if user is authorized to view this referral
    if (referral.referrer._id.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        error: 'Not authorized to access this referral'
      })
    }

    res.json({
      success: true,
      referral
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

// Update referral status (admin only)
router.patch('/:id/status', protect, authorize('admin'), [
  body('status')
    .isIn(['pending', 'active', 'completed', 'cancelled'])
    .withMessage('Invalid status')
], async (req, res) => {
  try {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }

    const referral = await Referral.findById(req.params.id)
    if (!referral) {
      return res.status(404).json({
        success: false,
        error: 'Referral not found'
      })
    }

    referral.status = req.body.status
    if (req.body.status === 'completed') {
      referral.paymentStatus = 'paid'
      referral.paymentDate = Date.now()

      // Update referrer's wallet
      const referrer = await User.findById(referral.referrer)
      referrer.wallet.balance += referral.commission
      await referrer.save()
    }

    await referral.save()

    res.json({
      success: true,
      referral
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    })
  }
})

module.exports = router 