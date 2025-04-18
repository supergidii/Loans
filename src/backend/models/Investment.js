const mongoose = require('mongoose')

const investmentSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'User ID is required']
  },
  amount: {
    type: Number,
    required: [true, 'Investment amount is required'],
    min: [100, 'Minimum investment amount is $100'],
    max: [1000000, 'Maximum investment amount is $1,000,000']
  },
  duration: {
    type: Number,
    required: [true, 'Investment duration is required'],
    enum: {
      values: [4, 8, 16, 30],
      message: 'Duration must be either 4, 8, 16, or 30 days'
    }
  },
  interestRate: {
    type: Number,
    default: 10,
    min: [5, 'Minimum interest rate is 5%'],
    max: [20, 'Maximum interest rate is 20%']
  },
  expectedReturn: {
    type: Number,
    required: [true, 'Expected return is required']
  },
  status: {
    type: String,
    enum: ['pending', 'active', 'completed', 'cancelled'],
    default: 'pending'
  },
  startDate: {
    type: Date,
    default: Date.now
  },
  endDate: {
    type: Date,
    required: [true, 'End date is required']
  },
  referralCode: {
    type: String,
    default: ''
  },
  referredBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    default: null
  }
}, {
  timestamps: true
})

// Calculate expected return and end date before saving
investmentSchema.pre('save', function(next) {
  try {
    // Calculate expected return
    const dailyRate = 0.01; // 1% per day
    this.expectedReturn = this.amount * (1 + (dailyRate * this.duration));
    
    // Set end date based on duration
    this.endDate = new Date(Date.now() + (this.duration * 24 * 60 * 60 * 1000));
    
    next();
  } catch (error) {
    next(error);
  }
});

const Investment = mongoose.model('Investment', investmentSchema)

module.exports = Investment 