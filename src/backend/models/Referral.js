const mongoose = require('mongoose')

const referralSchema = new mongoose.Schema({
  referrer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  referred: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'active', 'completed', 'cancelled'],
    default: 'pending'
  },
  commission: {
    type: Number,
    default: 0
  },
  commissionRate: {
    type: Number,
    required: true
  },
  investment: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Investment'
  },
  paymentStatus: {
    type: String,
    enum: ['pending', 'paid', 'failed'],
    default: 'pending'
  },
  paymentDate: {
    type: Date
  },
  notes: String
}, {
  timestamps: true
})

// Update referrer's stats when referral is created
referralSchema.post('save', async function() {
  const User = mongoose.model('User')
  const referrer = await User.findById(this.referrer)
  
  if (this.status === 'active') {
    referrer.referralStats.activeReferrals += 1
    referrer.referralStats.totalReferrals += 1
  }
  
  if (this.status === 'completed') {
    referrer.referralStats.totalEarnings += this.commission
  }
  
  await referrer.save()
})

// Calculate commission based on investment amount
referralSchema.methods.calculateCommission = function(investmentAmount) {
  this.commission = investmentAmount * (this.commissionRate / 100)
  return this.commission
}

module.exports = mongoose.model('Referral', referralSchema) 