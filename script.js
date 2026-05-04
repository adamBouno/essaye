const form = document.getElementById('contactForm');
const formMessage = document.getElementById('formMessage');

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const name = formData.get('name');

  formMessage.textContent = `Merci ${name}, votre demande a bien été reçue ! Nous vous recontacterons très vite.`;
  formMessage.style.color = '#1d4f91';
  form.reset();
});
