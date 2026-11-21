// User roles and authentication types matching database/init.sql and Authorization Service

export type UserRole = 'ADMIN' | 'SALES' | 'SERVICE';

export interface User {
    id: string;
    email: string;
    fullName: string;
    role: UserRole;
    isActive: boolean;
    failedLoginAttempts?: number;
    lockedUntil?: string | null;
}

export interface LoginRequest {
    usernameOrEmail: string;
    password: string;
}

export interface LoginResponse {
    success: boolean;
    token?: string;
    user?: User;
    message?: string;
}

export interface PermissionCheckResult {
    allowed: boolean;
    reason?: string;
    statusCode: 200 | 403;
    message: string;
}
