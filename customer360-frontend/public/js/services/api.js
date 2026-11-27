const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;

export class ApiError extends Error {
    constructor(status, detail, code) {
        super(detail);
        this.name = 'ApiError';
        this.status = status;
        this.code = code;
    }
}

async function request(path, { token, ...options } = {}) {
    const headers = new Headers(options.headers || {});
    headers.set('Accept', 'application/json');
    if (options.body) headers.set('Content-Type', 'application/json');
    if (token) headers.set('Authorization', `Bearer ${token}`);

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new ApiError(
            response.status,
            body.detail || body.message || 'Yêu cầu không thành công.',
            body.code
        );
    }
    return body;
}

export const ApiService = {
    async login(email, password) {
        try {
            const data = await request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            return { ...data, success: true };
        } catch (error) {
            return {
                success: false,
                message: error instanceof Error
                    ? error.message
                    : 'Không thể kết nối dịch vụ đăng nhập.'
            };
        }
    },

    searchAccounts(query, token) {
        const params = new URLSearchParams();
        if (query?.trim()) params.set('q', query.trim());
        const suffix = params.size ? `?${params.toString()}` : '';
        return request(`/accounts/search${suffix}`, { token });
    },

    getAccount(accountId, token) {
        return request(`/accounts/${encodeURIComponent(accountId)}`, { token });
    },

    getLatestBriefing(accountId, token) {
        return request(
            `/accounts/${encodeURIComponent(accountId)}/briefings/latest`,
            { token }
        );
    },

    generateBriefing(accountId, siteId, token) {
        return request('/briefings/generate', {
            method: 'POST',
            token,
            body: JSON.stringify({
                account_id: accountId,
                site_id: siteId || null
            })
        });
    },

    getBriefing(briefingId, token) {
        return request(`/briefings/${encodeURIComponent(briefingId)}`, { token });
    },

    getBriefingCitations(briefingId, token) {
        return request(
            `/briefings/${encodeURIComponent(briefingId)}/citations`,
            { token }
        );
    }
};
