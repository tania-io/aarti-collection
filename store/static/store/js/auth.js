document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // Toggle Password Visibility
    // ==========================

    document.querySelectorAll(".toggle-password").forEach(button => {

        button.addEventListener("click", () => {

            const input = button.previousElementSibling;

            if (!input) return;

            if (input.type === "password") {
                input.type = "text";
                button.textContent = "🙈";
            } else {
                input.type = "password";
                button.textContent = "👁";
            }

        });

    });

    // ==========================
    // Password Match Checker
    // (Register Page)
    // ==========================

    const password = document.getElementById("password");
    const confirm = document.getElementById("confirm_password");
    const message = document.getElementById("passwordMatch");

    if (password && confirm && message) {

        function checkPasswordMatch() {

            if (confirm.value === "") {
                message.textContent = "";
                return;
            }

            if (password.value === confirm.value) {
                message.textContent = "✓ Passwords match";
                message.style.color = "green";
            } else {
                message.textContent = "✗ Passwords do not match";
                message.style.color = "crimson";
            }

        }

        password.addEventListener("input", checkPasswordMatch);
        confirm.addEventListener("input", checkPasswordMatch);

    }

});