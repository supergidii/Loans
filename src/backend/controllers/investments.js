const Investment = require('../models/Investment');
const Transaction = require('../models/Transaction');
const { validationResult } = require('express-validator');

// @desc    Get all investments
// @route   GET /api/investments
// @access  Public
exports.getInvestments = async (req, res) => {
  try {
    const investments = await Investment.find()
      .populate('user', 'firstName lastName email')
      .sort('-createdAt');

    res.json({
      success: true,
      count: investments.length,
      data: investments
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
};

// @desc    Get single investment
// @route   GET /api/investments/:id
// @access  Public
exports.getInvestment = async (req, res) => {
  try {
    const investment = await Investment.findById(req.params.id)
      .populate('user', 'firstName lastName email');

    if (!investment) {
      return res.status(404).json({
        success: false,
        error: 'Investment not found'
      });
    }

    res.json({
      success: true,
      data: investment
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
};

// @desc    Create new investment
// @route   POST /api/investments
// @access  Private
exports.createInvestment = async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { amount, type, duration, interestRate } = req.body;

    // Create investment
    const investment = await Investment.create({
      user: req.user.id,
      amount,
      type,
      duration,
      interestRate
    });

    // Create transaction record
    await Transaction.create({
      user: req.user.id,
      investment: investment._id,
      type: 'investment',
      amount,
      status: 'completed',
      description: `Investment in ${type} plan`,
      paymentMethod: 'system'
    });

    res.status(201).json({
      success: true,
      data: investment
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
};

// @desc    Update investment
// @route   PUT /api/investments/:id
// @access  Private/Admin
exports.updateInvestment = async (req, res) => {
  try {
    let investment = await Investment.findById(req.params.id);

    if (!investment) {
      return res.status(404).json({
        success: false,
        error: 'Investment not found'
      });
    }

    investment = await Investment.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });

    res.json({
      success: true,
      data: investment
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
};

// @desc    Delete investment
// @route   DELETE /api/investments/:id
// @access  Private/Admin
exports.deleteInvestment = async (req, res) => {
  try {
    const investment = await Investment.findById(req.params.id);

    if (!investment) {
      return res.status(404).json({
        success: false,
        error: 'Investment not found'
      });
    }

    await investment.remove();

    res.json({
      success: true,
      data: {}
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
};

// @desc    Get user investments
// @route   GET /api/investments/user/me
// @access  Private
exports.getUserInvestments = async (req, res) => {
  try {
    const investments = await Investment.find({ user: req.user.id })
      .sort('-createdAt');

    res.json({
      success: true,
      count: investments.length,
      data: investments
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
}; 