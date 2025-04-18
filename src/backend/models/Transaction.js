const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.ObjectId,
    ref: 'User',
    required: true
  },
  investment: {
    type: mongoose.Schema.ObjectId,
    ref: 'Investment'
  },
  type: {
    type: String,
    enum: ['deposit', 'withdrawal', 'interest', 'referral_bonus', 'investment'],
    required: true
  },
  amount: {
    type: Number,
    required: [true, 'Please provide transaction amount']
  },
  status: {
    type: String,
    enum: ['pending', 'completed', 'failed', 'cancelled'],
    default: 'pending'
  },
  description: {
    type: String,
    required: [true, 'Please provide transaction description']
  },
  reference: {
    type: String,
    unique: true
  },
  paymentMethod: {
    type: String,
    enum: ['bank_transfer', 'credit_card', 'debit_card', 'crypto', 'system'],
    required: true
  },
  metadata: {
    type: Map,
    of: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Generate unique reference before saving
transactionSchema.pre('save', function(next) {
  if (!this.reference) {
    this.reference = 'TXN' + Math.random().toString(36).substring(2, 15).toUpperCase();
  }
  next();
});

module.exports = mongoose.model('Transaction', transactionSchema); 