const mongoose = require('mongoose')

const pairedUserSchema = new mongoose.Schema({
  user1: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'First user ID is required']
  },
  user2: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Second user ID is required']
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
    type: Date
  },
  pairingType: {
    type: String,
    enum: ['investment', 'referral', 'manual'],
    required: [true, 'Pairing type is required']
  },
  notes: {
    type: String
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Creator ID is required']
  },
  investment: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Investment'
  },
  referral: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Referral'
  }
}, {
  timestamps: true
})

// Ensure user1 and user2 are different
pairedUserSchema.pre('validate', function(next) {
  if (this.user1 && this.user2 && this.user1.toString() === this.user2.toString()) {
    next(new Error('User1 and User2 cannot be the same user'))
  } else {
    next()
  }
})

// Create a compound index to prevent duplicate pairings
pairedUserSchema.index({ user1: 1, user2: 1, status: 1 }, { unique: true })

module.exports = mongoose.model('PairedUser', pairedUserSchema) 