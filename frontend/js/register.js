const registerForm = document.getElementById("register-form");
const message = document.getElementById("message");

registerForm.addEventListener("submit", async (event) => {
event.preventDefault();


const email = document.getElementById("email").value.trim();
const password = document.getElementById("password").value;
const submitButton = registerForm.querySelector(
    'button[type="submit"]'
);

message.textContent = "";
message.className = "form-message";

submitButton.disabled = true;
submitButton.textContent = "Creating account...";

try {
    const user = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify({
            email: email,
            password: password,
        }),
    });

    message.textContent = "Account created successfully! Redirecting...";
    message.classList.add("success");

    registerForm.reset();

    setTimeout(() => {
        window.location.href = "/login";
    }, 1200);

} catch (error) {
    message.textContent = error.message;
    message.classList.add("error");

} finally {
    submitButton.disabled = false;
    submitButton.textContent = "Create account";
}


});
