// Native fetch-based API client (no axios dependency)
// Mirrors the axios response shape: { data, status } so consumers need no changes.

const BASE_URL = '';  // relative — goes through Vite proxy in dev, same-origin in prod

function getHeaders(extraHeaders = {}) {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...extraHeaders,
    };
}

async function handleResponse(response) {
    if (response.status === 401) {
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(new Error('Unauthorized'));
    }

    if (!response.ok) {
        // Try to parse error detail the way axios does
        let detail;
        try {
            const errData = await response.json();
            detail = errData.detail || JSON.stringify(errData);
        } catch {
            detail = response.statusText;
        }
        const err = new Error(detail);
        err.response = { status: response.status, data: { detail } };
        return Promise.reject(err);
    }

    // Parse JSON body (or empty for 204)
    let data = null;
    if (response.status !== 204) {
        try { data = await response.json(); } catch { data = null; }
    }

    return { data, status: response.status };
}

const api = {
    async get(url, config = {}) {
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'GET',
            headers: getHeaders(config.headers),
        });
        return handleResponse(response);
    },

    async post(url, body = null, config = {}) {
        // Support URLSearchParams (for form-urlencoded login)
        const isFormData = body instanceof URLSearchParams;
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'POST',
            headers: isFormData
                ? {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    ...(localStorage.getItem('token')
                        ? { Authorization: `Bearer ${localStorage.getItem('token')}` }
                        : {}),
                    ...(config.headers || {}),
                }
                : getHeaders(config.headers),
            body: isFormData ? body.toString() : (body !== null ? JSON.stringify(body) : undefined),
        });
        return handleResponse(response);
    },

    async delete(url, config = {}) {
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'DELETE',
            headers: getHeaders(config.headers),
        });
        return handleResponse(response);
    },
};

export default api;

