const db = require('../config/database');

// Check if user has required role
exports.requireRole = (...allowedRoles) => {
    return (req, res, next) => {
        const userRole = req.user.role;

        if (!allowedRoles.includes(userRole)) {
            return res.status(403).json({
                error: 'Access denied',
                message: `This action requires one of the following roles: ${allowedRoles.join(', ')}`
            });
        }

        next();
    };
};

// Check if Project Manager or Site Supervisor is assigned to a project
exports.requireProjectAccess = async (req, res, next) => {
    try {
        const userRole = req.user.role;
        const workerId = req.user.worker_id;
        const projectId = req.params.id || req.body.project_id;

        if (!projectId) {
            return res.status(400).json({ error: 'Project ID is required for this action' });
        }

        // Admins can access everything
        if (userRole === 'Admin') {
            return next();
        }

        const assignmentCheckRoles = ['Project Manager', 'Site Supervisor'];

        if (!assignmentCheckRoles.includes(userRole)) {
            return res.status(403).json({
                error: 'Access denied',
                message: 'Your role is not authorized for this action'
            });
        }

        if (!workerId) {
            return res.status(403).json({
                error: 'Access denied',
                message: 'Assigned worker information is missing for this user'
            });
        }

        const [assignments] = await db.query(
            'SELECT * FROM v_project_worker_assignments WHERE project_id = ? AND worker_id = ?',
            [projectId, workerId]
        );

        if (assignments.length === 0) {
            const roleSpecificMessage =
                userRole === 'Project Manager'
                    ? 'You are not assigned to this project'
                    : 'You can only access projects you are assigned to';

            return res.status(403).json({
                error: 'Access denied',
                message: roleSpecificMessage
            });
        }

        next();
    } catch (error) {
        console.error('Project access check error:', error);
        res.status(500).json({ error: 'Authorization check failed' });
    }
};