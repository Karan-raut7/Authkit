const API_BASE_URL = "http://127.0.0.1:8000/v1";

async function apiRequest(endpoint, options = {}) {
    const accessToken = sessionStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
    }

    const requestUrl = endpoint === "/me"
    ? "http://127.0.0.1:8000/me"
    : `${API_BASE_URL}${endpoint}`;

let response = await fetch(requestUrl, {
        ...options,
        headers,
    });

    // If the access token expired, try refreshing it.
    if (
    response.status === 401 &&
    endpoint !== "/auth/refresh" &&
    endpoint !== "/auth/login"
) {
        const refreshed = await refreshAccessToken();

        if (refreshed) {
            const newHeaders = {
                "Content-Type": "application/json",
                ...options.headers,
                Authorization: `Bearer ${sessionStorage.getItem("access_token")}`,
            };

            response = await fetch(requestUrl, {
                ...options,
                headers: newHeaders,
            });
        } else {
            sessionStorage.removeItem("access_token");
            sessionStorage.removeItem("refresh_token");
            window.location.replace("/login");

            throw new Error("Your session has expired. Please log in again.");
        }
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || data.message || "Something went wrong."
        );
    }

    return data;
}

async function refreshAccessToken() {
    const refreshToken = sessionStorage.getItem("refresh_token");

    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                refresh_token: refreshToken,
            }),
        });

        if (!response.ok) {
            return false;
        }

        const tokens = await response.json();

        sessionStorage.setItem("access_token", tokens.access_token);
        sessionStorage.setItem("refresh_token", tokens.refresh_token);

        return true;
    } catch (error) {
        console.error("Token refresh failed:", error);
        return false;
    }
}