function showForm(type) {
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');

    if (type === 'register') {
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    } else {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    }
}

document.addEventListener("DOMContentLoaded", () => {
    showForm('login'); // Показываем логин по умолчанию
});

async function submitForm(event, endpoint) {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form).entries());

    // Удалим прошлые ошибки
    document.querySelectorAll('.error-message').forEach(el => el.remove());

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
        if (result.detail) {
            // Pydantic ошибки (валидаторы FastAPI)
            result.detail.forEach(err => {
                const fieldName = err.loc.at(-1); // более надёжно
                const message = err.msg;

                const input = form.querySelector(`[name="${fieldName}"]`);
                if (input) {
                    const error = document.createElement("div");
                    error.className = "error-message";
                    error.style.color = "red";
                    error.style.fontSize = "0.9em";
                    error.style.marginTop = "4px";
                    error.textContent = message;
                    input.insertAdjacentElement("afterend", error);
                }
            });
        } else if (result.error) {
            // Твои кастомные ошибки (например, "Пользователь уже существует")
            const error = document.createElement("div");
            error.className = "error-message";
            error.style.color = "red";
            error.style.marginBottom = "8px";
            error.textContent = result.error;
            form.prepend(error);
        }
    } else {
        alert("Успешная регистрация!");
        // Можно сбросить форму или сделать редирект
        form.reset();
    }
}
