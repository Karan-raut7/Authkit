const emailElement = document.getElementById("user-email");
const messageElement = document.getElementById("dashboard-message");
const logoutButton = document.getElementById("logout-button");

async function loadDashboard() {
const accessToken = sessionStorage.getItem("access_token");


if (!accessToken) {
    window.location.replace("/login");
    return;
}

try {
    const user = await apiRequest("/me");


    emailElement.textContent = user.email;

} catch (error) {
    if (error.message) {
        messageElement.textContent = error.message;
        messageElement.classList.add("error");
    }

    console.error("Dashboard error:", error);
}



}

logoutButton.addEventListener("click", async () => {
    const refreshToken = sessionStorage.getItem("refresh_token");

    logoutButton.disabled = true;
    logoutButton.textContent = "Logging out...";

    try {
        if (refreshToken) {
            await apiRequest("/auth/logout", {
                method: "POST",
                body: JSON.stringify({
                    refresh_token: refreshToken,
                }),
            });
        }
    } catch (error) {
        console.error("Backend logout failed:", error.message);
    } finally {
        sessionStorage.removeItem("access_token");
        sessionStorage.removeItem("refresh_token");

        window.location.replace("/login");
    }
});

loadDashboard();
