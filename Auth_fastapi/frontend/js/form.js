function showForm(type) {
  const register = document.getElementById('register-form');
  const login = document.getElementById('login-form');
  const buttons = document.querySelectorAll('.cont_button');

  if (type === 'register') {
    register.classList.remove('hidden');
    login.classList.add('hidden');
  } else {
    register.classList.add('hidden');
    login.classList.remove('hidden');
  }
}
document.addEventListener('DOMContentLoaded', () => {
  showForm('login');
  submit();
});

async function sendData(form, endpoint, object) {
  form.querySelectorAll('.error-message').forEach((el) => el.remove());

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(object),
  });

  const result = await response.json();

  if (!response.ok) {
    if (result.detail) {
      result.detail.forEach((err) => {
        const fieldName = err.loc.at(-1);
        const message = err.msg;
        const input = form.querySelector(`[name="${fieldName}"]`);
        if (input) {
          const error = document.createElement('div');
          error.className = 'error-message';
          error.style.color = 'red';
          error.style.fontSize = '0.9em';
          error.style.marginTop = '4px';
          error.textContent = message;
          input.insertAdjacentElement('afterend', error);
        }
      });
    } else if (result.error) {
      const error = document.createElement('div');
      error.className = 'error-message';
      error.style.color = 'red';
      error.style.marginBottom = '8px';
      error.textContent = result.error;
      form.prepend(error);
    }
  } else {
    alert('Успешная регистрация!');
    form.reset();
  }
}

function submit() {
  const forms = document.querySelectorAll('form');
  forms.forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!form.classList.contains('hidden')) {
        const object = Object.fromEntries(new FormData(form).entries());
        const endpoint = form.dataset.endpoint;
        sendData(form, endpoint, object);
      }
    });
  });
}
