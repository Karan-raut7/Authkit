const changePasswordForm = document.getElementById("change-password-form");

const currentPasswordInput = document.getElementById("current-password");
const newPasswordInput = document.getElementById("new-password");
const confirmPasswordInput = document.getElementById("confirm-password");

const togglePasswords = document.getElementById("toggle-passwords");
const changePasswordButton = document.getElementById("change-password-button");
const changePasswordMessage = document.getElementById("change-password-message");

// Show or hide all password fields.
togglePasswords.addEventListener("change", () => {
    const inputType = togglePasswords.checked ? "text" : "password";

    currentPasswordInput.type = inputType;
    newPasswordInput.type = inputType;
    confirmPasswordInput.type = inputType;
});

changePasswordForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const currentPassword = currentPasswordInput.value;
    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    changePasswordMessage.textContent = "";
    changePasswordMessage.classList.remove("success", "error");

    // Check that the new password matches its confirmation.
    if (newPassword !== confirmPassword) {
        changePasswordMessage.textContent = "The new passwords do not match.";
        changePasswordMessage.classList.add("error");
        return;
    }

    // Prevent reusing the current password.
    if (newPassword === currentPassword) {
        changePasswordMessage.textContent =
            "Your new password must differ from your current password.";

        changePasswordMessage.classList.add("error");
        return;
    }

    changePasswordButton.disabled = true;
    changePasswordButton.textContent = "Updating password...";

    try {
        const response = await apiRequest("/auth/change-password", {
            method: "PATCH",
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
            }),
        });

        changePasswordMessage.textContent =
            response.message || "Password changed successfully.";

        changePasswordMessage.classList.add("success");

        // The backend revokes all refresh tokens, so end this session.
        sessionStorage.removeItem("access_token");
        sessionStorage.removeItem("refresh_token");

        changePasswordForm.reset();

        // Give the user a moment to read the success message.
        setTimeout(() => {
            window.location.replace("/login");
        }, 1800);

    } catch (error) {
        changePasswordMessage.textContent =
            error.message || "Unable to change your password.";

        changePasswordMessage.classList.add("error");

    } finally {
        changePasswordButton.disabled = false;
        changePasswordButton.textContent = "Update password";
    }
});