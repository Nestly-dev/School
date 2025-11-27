const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// Basic request payload validation to fail fast on obviously bad inputs
const validatePayload = (requiredFields) => (req, res, next) => {
    const missing = requiredFields.filter((field) => {
        const value = req.body[field];
        return value === undefined || value === null || value === '';
    });

    if (missing.length > 0) {
        return res.status(400).json({
            error: `Missing required fields: ${missing.join(', ')}`
        });
    }

    next();
};

// POST /api/auth/register - Register new user
router.post(
    '/register',
    validatePayload(['email', 'password', 'role']),
    authController.register
);

// POST /api/auth/login - Login user
router.post(
    '/login',
    validatePayload(['email', 'password']),
    authController.login
);

module.exports = router;