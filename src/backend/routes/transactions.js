const express = require('express');
const router = express.Router();
const { protect, authorize } = require('../middleware/auth');
const {
  getTransactions,
  getTransaction,
  createTransaction,
  updateTransaction,
  getUserTransactions
} = require('../controllers/transactions');

// Public routes
router.get('/', getTransactions);
router.get('/:id', getTransaction);

// Protected routes
router.use(protect);
router.post('/', createTransaction);
router.get('/user/me', getUserTransactions);

// Admin routes
router.use(authorize('admin'));
router.put('/:id', updateTransaction);

module.exports = router; 