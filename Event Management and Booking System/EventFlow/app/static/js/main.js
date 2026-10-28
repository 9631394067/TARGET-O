// ===================== NAVBAR SCROLL =====================
const navbar = document.querySelector('.navbar');
const backToTop = document.querySelector('.back-to-top');

window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    navbar?.classList.add('scrolled');
    backToTop?.classList.add('visible');
  } else {
    navbar?.classList.remove('scrolled');
    backToTop?.classList.remove('visible');
  }
});

backToTop?.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ===================== FLASH MESSAGES =====================
document.querySelectorAll('.flash-close').forEach(btn => {
  btn.addEventListener('click', () => {
    const msg = btn.closest('.flash-msg');
    msg.style.opacity = '0';
    msg.style.transform = 'translateX(100px)';
    msg.style.transition = 'all 0.3s ease';
    setTimeout(() => msg.remove(), 300);
  });
});

// Auto-dismiss flash messages after 5s
setTimeout(() => {
  document.querySelectorAll('.flash-msg').forEach((msg, i) => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(100px)';
      msg.style.transition = 'all 0.3s ease';
      setTimeout(() => msg.remove(), 300);
    }, i * 200);
  });
}, 5000);

// ===================== HAMBURGER MENU =====================
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger?.addEventListener('click', () => {
  navLinks?.classList.toggle('mobile-open');
  hamburger.classList.toggle('active');
});

// ===================== TICKET COUNTER =====================
function initTicketCounter() {
  const counter = document.querySelector('.ticket-counter');
  if (!counter) return;

  const input = counter.querySelector('input');
  const minusBtn = counter.querySelector('.minus');
  const plusBtn = counter.querySelector('.plus');
  const maxVal = parseInt(input?.max || 10);
  const minVal = parseInt(input?.min || 1);
  const pricePerTicket = parseFloat(document.getElementById('price-per-ticket')?.dataset.price || 0);
  const totalEl = document.getElementById('total-price');

  function updateTotal() {
    const val = parseInt(input.value) || 1;
    if (totalEl && pricePerTicket > 0) {
      totalEl.textContent = `₹${(val * pricePerTicket).toLocaleString('en-IN')}`;
    } else if (totalEl) {
      totalEl.textContent = 'FREE';
    }
  }

  minusBtn?.addEventListener('click', () => {
    const val = parseInt(input.value) || 1;
    if (val > minVal) { input.value = val - 1; updateTotal(); }
  });

  plusBtn?.addEventListener('click', () => {
    const val = parseInt(input.value) || 1;
    if (val < maxVal) { input.value = val + 1; updateTotal(); }
  });

  input?.addEventListener('change', () => {
    let val = parseInt(input.value) || 1;
    val = Math.max(minVal, Math.min(maxVal, val));
    input.value = val;
    updateTotal();
  });

  updateTotal();
}

initTicketCounter();

// ===================== SCROLL REVEAL =====================
const revealEls = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('revealed');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

revealEls.forEach(el => observer.observe(el));

// ===================== IMAGE PREVIEW =====================
const imageInput = document.querySelector('input[type="file"][name="banner_image"]');
const imagePreview = document.getElementById('image-preview');

imageInput?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file && imagePreview) {
    const reader = new FileReader();
    reader.onload = (ev) => {
      imagePreview.src = ev.target.result;
      imagePreview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
});

// ===================== SEARCH DEBOUNCE =====================
let searchTimeout;
const searchInput = document.querySelector('.search-bar input[name="search"]');

searchInput?.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    searchInput.closest('form')?.submit();
  }, 700);
});

// ===================== ANIMATED NUMBERS =====================
function animateNumber(el, target, duration = 1500) {
  let start = 0;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start += step;
    if (start >= target) { start = target; clearInterval(timer); }
    el.textContent = Math.floor(start).toLocaleString('en-IN');
  }, 16);
}

const numEls = document.querySelectorAll('[data-count]');
const numObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.count);
      animateNumber(el, target);
      numObserver.unobserve(el);
    }
  });
});
numEls.forEach(el => numObserver.observe(el));

// ===================== CONFIRM DELETE =====================
document.querySelectorAll('.confirm-delete').forEach(form => {
  form.addEventListener('submit', (e) => {
    if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
      e.preventDefault();
    }
  });
});

// ===================== COPY BOOKING REF =====================
document.querySelectorAll('.copy-ref').forEach(btn => {
  btn.addEventListener('click', () => {
    const ref = btn.dataset.ref;
    navigator.clipboard.writeText(ref).then(() => {
      const orig = btn.textContent;
      btn.textContent = '✅ Copied!';
      setTimeout(() => btn.textContent = orig, 2000);
    });
  });
});

console.log('%c⚡ EventFlow', 'color: #7c3aed; font-size: 1.5rem; font-weight: 900;');
console.log('%cBuilt with ❤️ | Premium Event Management System', 'color: #06b6d4;');
