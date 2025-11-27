const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET;

// Verify JWT token
exports.authenticateToken = (req, res, next) => {
    if (!JWT_SECRET) {
        console.error('JWT_SECRET is not configured. Rejecting authenticated request.');
        return res.status(500).json({ error: 'Authentication is temporarily unavailable' });
    }

    // Get token from Authorization header
    const authHeader = req.headers.authorization || req.headers.Authorization;
    const token = authHeader && authHeader.split(' ')[1]; // Format: "Bearer TOKEN"

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    try {
        // Verify token
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = decoded; // Attach user info to request
        next();
    } catch (error) {
        return res.status(403).json({ error: 'Invalid or expired token' });
    }
};