# Referral Investment System

A modern, responsive referral investment system with an admin dashboard, built with Vue.js, Express, and MongoDB.

## Features

- User authentication and authorization
- Investment management
- Referral system with commission tracking
- Admin dashboard with comprehensive controls
- Real-time statistics and reporting
- Responsive design for all devices
- Secure payment processing
- Email notifications

## Prerequisites

- Node.js (v14 or higher)
- MongoDB (v4.4 or higher)
- npm or yarn package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd referral-investment-system
```

2. Install backend dependencies:
```bash
npm install
```

3. Install frontend dependencies:
```bash
cd src/frontend
npm install
```

4. Create a `.env` file in the root directory and configure your environment variables:
```env
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb://localhost:27017/referral-investment
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRE=30d
EMAIL_SERVICE=gmail
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
EMAIL_FROM=your_email@gmail.com
FRONTEND_URL=http://localhost:8080
```

5. Start the development servers:

Backend:
```bash
npm run dev
```

Frontend:
```bash
cd src/frontend
npm run serve
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000

## Project Structure

```
referral-investment-system/
├── src/
│   ├── frontend/
│   │   ├── components/
│   │   ├── views/
│   │   ├── store/
│   │   ├── router/
│   │   └── assets/
│   ├── backend/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── config/
│   ├── public/
│   └── assets/
├── .env
├── package.json
└── README.md
```

## API Documentation

### Authentication
- POST /api/auth/register - Register a new user
- POST /api/auth/login - Login user
- GET /api/auth/user - Get current user
- POST /api/auth/forgot-password - Request password reset
- POST /api/auth/reset-password/:token - Reset password

### Investments
- GET /api/investments - Get all investments (admin)
- GET /api/investments/my-investments - Get user's investments
- GET /api/investments/stats - Get investment statistics
- POST /api/investments - Create new investment
- GET /api/investments/:id - Get single investment
- PATCH /api/investments/:id/status - Update investment status (admin)

### Referrals
- GET /api/referrals - Get all referrals (admin)
- GET /api/referrals/my-referrals - Get user's referrals
- GET /api/referrals/stats - Get referral statistics
- POST /api/referrals/generate-code - Generate referral code
- GET /api/referrals/:id - Get single referral
- PATCH /api/referrals/:id/status - Update referral status (admin)

### Admin
- GET /api/admin/dashboard - Get dashboard statistics
- GET /api/admin/users - Get all users
- PATCH /api/admin/users/:id - Update user
- GET /api/admin/settings - Get system settings
- PATCH /api/admin/settings - Update system settings
- GET /api/admin/logs - Get system logs

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization
- CORS protection
- Rate limiting
- Secure password reset flow
- Email verification

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@example.com or create an issue in the repository. 