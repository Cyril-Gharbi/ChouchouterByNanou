
document.addEventListener('DOMContentLoaded', () => {
  // Email validation
  const email = document.querySelector('input[name="email"]');
  if (email) {
    email.addEventListener('input', () => {
      email.setCustomValidity(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value) ? '' : 'Adresse e-mail invalide');
      email.reportValidity();
    })
  }

  // Password robustness indicator
  const pwd = document.querySelector('input[name="password"]');
  if (pwd) {
    const meter = document.createElement('div');
    meter.className = 'form-text';
    pwd.insertAdjacentElement('afterend', meter);
    pwd.addEventListener('input', () => {
      const v = pwd.value;
      const strength = [/.{8,}/, /[A-Z]/, /[a-z]/, /\d/, /[^A-Za-z0-9]/].reduce((s, r) => s + (r.test(v) ? 1 : 0), 0);
      const labels = ['Très faible', 'Faible', 'Moyen', 'Bon', 'Fort', 'Excellent'];
      meter.textContent = 'Sécurité du mot de passe : ' + labels[strength];
    });
  }

  // RGPD: enable/disable the submit
  const form = document.querySelector('form.login-form');
  if (form) {
    const consent = form.querySelector('input[name="consent_privacy"]');
    const submit = form.querySelector('button[type="submit"], input[type="submit"]') || form.querySelector('button, input[type="submit"]');
    const toggle = () => { if (submit) submit.disabled = consent && !consent.checked; };
    toggle();
    if (consent) consent.addEventListener('change', toggle);
  }
});
