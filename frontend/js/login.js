const loginForm = document.getElementById("login-form");
const message = document.getElementById("message");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const submitButton = loginForm.querySelector(
        'button[type="submit"]'
    );

    message.textContent = "";
    message.className = "form-message";

    submitButton.disabled = true;
    submitButton.textContent = "Logging in...";

    try {
        const tokens = await apiRequest("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        });

        console.log("Login successful:", tokens);

        sessionStorage.setItem("access_token", tokens.access_token);
        sessionStorage.setItem("refresh_token", tokens.refresh_token);

        console.log("Redirecting to dashboard...");
        window.location.href = "/dashboard";

    } catch (error) {
    console.error("Login failed:", error);

    message.textContent = error.message;
    message.className = "form-message error";

} finally {
        submitButton.disabled = false;
        submitButton.textContent = "Log in";
    }
});