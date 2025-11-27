const mysql = require('mysql2');
require('dotenv').config();

const REQUIRED_DB_VARS = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'];
const missingDbVars = REQUIRED_DB_VARS.filter((key) => !process.env[key]);

if (missingDbVars.length > 0) {
    throw new Error(`Missing database environment variables: ${missingDbVars.join(', ')}`);
}

// Create connection pool (better than single connection)
const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    port: Number(process.env.DB_PORT) || 3306,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// Surface unexpected pool errors instead of silently swallowing them
pool.on('error', (err) => {
    console.error('Unexpected database pool error:', err);
});

// Use promises instead of callbacks
const promisePool = pool.promise();

module.exports = promisePool;