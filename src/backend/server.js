const express = require('express')
const mongoose = require('mongoose')
const cors = require('cors')
const dotenv = require('dotenv')

// Load env vars
dotenv.config()

// Create Express app
const app = express()

// CORS configuration
const corsOptions = {
  origin: ['http://localhost:8080', 'http://localhost:8081', 'http://localhost:8082'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}

// Middleware
app.use(cors(corsOptions))
app.use(express.json())

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`, {
    headers: {
      authorization: req.headers.authorization ? 'Bearer [hidden]' : 'none',
      'content-type': req.headers['content-type']
    },
    body: req.body
  })
  next()
})

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/referral', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  dbName: 'referral' // Explicitly set the database name
})
.then(() => console.log('MongoDB Connected to database: referral'))
.catch(err => console.error('MongoDB connection error:', err))

// Routes
app.use('/api/auth', require('./routes/auth'))
app.use('/api/investments', require('./routes/investments'))
app.use('/api/referrals', require('./routes/referrals'))
app.use('/api/admin', require('./routes/admin'))

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).json({
    success: false,
    message: 'Something went wrong!',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  })
})

// Start server
const PORT = process.env.PORT || 5000
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
  console.log(`CORS enabled for origins: ${JSON.stringify(corsOptions.origin)}`)
}) 