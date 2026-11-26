// Adds a Show/Hide toggle to every password input on the page.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="password"]').forEach((input) => {
    const wrap = document.createElement('div');
    wrap.style.position = 'relative';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    input.style.paddingRight = '4.5rem';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = 'Show';
    btn.style.cssText =
      'position:absolute;right:.4rem;top:50%;transform:translateY(-50%);' +
      'background:none;border:none;color:#2563eb;font-size:.8rem;cursor:pointer;padding:.2rem .3rem';
    btn.addEventListener('click', () => {
      const showing = input.type === 'text';
      input.type = showing ? 'password' : 'text';
      btn.textContent = showing ? 'Show' : 'Hide';
    });
    wrap.appendChild(btn);
  });
});
