const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const db = require('../config/database');

const ALLOWED_ROLES = ['Admin', 'Project Manager', 'Site Supervisor'];

// Register new user
exports.register = async (req, res) => {
    try {
        const { email, password, role, preferred_language, worker_id } = req.body;

        // Validate input
        if (!email || !password || !role) {
            return res.status(400).json({ error: 'Email, password, and role are required' });
        }

        if (!ALLOWED_ROLES.includes(role)) {
            return res.status(400).json({
                error: 'Invalid role supplied',
                allowed_roles: ALLOWED_ROLES
            });
        }

        // Check if user already exists
        const [existingUsers] = await db.query(
            'SELECT user_id FROM users WHERE email = ?',
            [email]
        );

        if (existingUsers.length > 0) {
            return res.status(409).json({ error: 'User already exists' });
        }

        if (worker_id) {
            const [workers] = await db.query(
                'SELECT worker_id FROM workers WHERE worker_id = ?',
                [worker_id]
            );

            if (workers.length === 0) {
                return res.status(400).json({ error: 'Invalid worker_id provided' });
            }
        }

        // Hash password (10 salt rounds is standard)
        const password_hash = await bcrypt.hash(password, 10);

        // Insert new user
        const [result] = await db.query(
            'INSERT INTO users (email, password_hash, role, preferred_language, worker_id) VALUES (?, ?, ?, ?, ?)',
            [email, password_hash, role, preferred_language || 'en', worker_id || null]
        );

        res.status(201).json({
            message: 'User registered successfully',
            user_id: result.insertId
        });

    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ error: 'Registration failed' });
    }
};

// Login user
exports.login = async (req, res) => {
    try {
        const { email, password } = req.body;

        // Validate input
        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password are required' });
        }

        // Find user by email
        const [users] = await db.query(
            'SELECT user_id, email, password_hash, role, preferred_language, worker_id FROM users WHERE email = ?',
            [email]
        );

        if (users.length === 0) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const user = users[0];

        // Check password
        const passwordMatch = await bcrypt.compare(password, user.password_hash);

        if (!passwordMatch) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // Generate JWT token
        const token = jwt.sign(
            {
                user_id: user.user_id,
                email: user.email,
                role: user.role,
                worker_id: user.worker_id
            },
            process.env.JWT_SECRET,
            { expiresIn: '24h' } // Token expires in 24 hours
        );

        res.json({
            message: 'Login successful',
            token,
            user: {
                user_id: user.user_id,
                email: user.email,
                role: user.role,
                preferred_language: user.preferred_language
            }
        });

    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Login failed' });
    }
};