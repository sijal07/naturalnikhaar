// 🎨 PREMIUM ANIMATIONS & INTERACTIVE EFFECTS

document.addEventListener('DOMContentLoaded', function() {
  // ===== SCROLL REVEAL ANIMATION =====
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('scroll-reveal');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all cards and sections
  document.querySelectorAll('.card, section, .container, .row > [class*="col-"]').forEach(el => {
    observer.observe(el);
  });

  // ===== HEADER SCROLL EFFECT =====
  const header = document.getElementById('header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      document.body.classList.add('scrolled');
    } else {
      document.body.classList.remove('scrolled');
    }
  });

  // ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#' && document.querySelector(href)) {
        e.preventDefault();
        document.querySelector(href).scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // ===== BUTTON RIPPLE EFFECT =====
  document.querySelectorAll('button, .btn, a.btn').forEach(button => {
    button.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';
      ripple.classList.add('ripple');

      if (this.querySelector('.ripple')) {
        this.querySelector('.ripple').remove();
      }

      this.appendChild(ripple);
    });
  });

  // ===== NAVBAR ANIMATION =====
  const navbar = document.querySelector('#navbar');
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach((link, index) => {
    link.style.animation = `slideInLeft 0.6s ease-out ${index * 0.1}s backwards`;
  });

  // ===== PARALLAX EFFECT =====
  window.addEventListener('scroll', () => {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    parallaxElements.forEach(el => {
      const speed = el.getAttribute('data-parallax') || 0.5;
      const yPos = window.scrollY * speed;
      el.style.transform = `translateY(${yPos}px)`;
    });
  });

  // ===== COUNTER ANIMATION =====
  const countElements = document.querySelectorAll('[data-count]');
  if (countElements.length > 0) {
    setTimeout(() => {
      countElements.forEach(el => {
        const target = parseInt(el.getAttribute('data-count'));
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;

        const timer = setInterval(() => {
          current += increment;
          if (current >= target) {
            el.textContent = target;
            clearInterval(timer);
          } else {
            el.textContent = Math.floor(current);
          }
        }, 16);
      });
    }, 500);
  }

  // ===== TOOLTIP INITIALIZATION =====
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(tooltip => {
    new bootstrap.Tooltip(tooltip);
  });

  // ===== FORM VALIDATION FEEDBACK =====
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!this.checkValidity()) {
        e.preventDefault();
        this.classList.add('was-validated');
      }
    });
  });

  // ===== INPUT FOCUS ANIMATION =====
  document.querySelectorAll('input, textarea, select').forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('focused');
    });

    input.addEventListener('blur', function() {
      this.parentElement.classList.remove('focused');
    });
  });

  // ===== LOADING STATE HANDLER =====
  document.querySelectorAll('[data-loading]').forEach(button => {
    button.addEventListener('click', function() {
      const originalText = this.innerHTML;
      this.disabled = true;
      this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';

      setTimeout(() => {
        this.disabled = false;
        this.innerHTML = originalText;
      }, 2000);
    });
  });

  // ===== SCROLL TO TOP BUTTON =====
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) {
        backToTop.classList.add('active');
        backToTop.style.display = 'flex';
      } else {
        backToTop.classList.remove('active');
        backToTop.style.display = 'none';
      }
    });

    backToTop.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // ===== CARD ANIMATION ON HOVER =====
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.zIndex = '10';
    });

    card.addEventListener('mouseleave', function() {
      this.style.zIndex = '0';
    });
  });

  // ===== TYPING ANIMATION =====
  const typeElements = document.querySelectorAll('[data-type]');
  typeElements.forEach(element => {
    const text = element.textContent;
    element.textContent = '';
    let index = 0;

    const typeChar = () => {
      if (index < text.length) {
        element.textContent += text[index];
        index++;
        setTimeout(typeChar, 50);
      }
    };

    typeChar();
  });

  // ===== DYNAMIC YEAR IN FOOTER =====
  const yearElement = document.getElementById('current-year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }

  // ===== NOTIFICATION TOAST =====
  function showNotification(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} notification-toast`;
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      max-width: 400px;
      z-index: 10000;
      animation: slideInRight 0.4s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideInRight 0.4s ease-out reverse';
      setTimeout(() => toast.remove(), 400);
    }, duration);
  }

  // Make notification globally available
  window.showNotification = showNotification;

  // ===== LAZY LOADING IMAGES =====
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src || img.src;
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }

  // ===== MOBILE MENU ANIMATION =====
  const hamburger = document.querySelector('.mobile-nav-toggle');
  if (hamburger) {
    hamburger.addEventListener('click', function() {
      this.classList.toggle('active');
    });
  }

  // ===== KEYBOARD NAVIGATION =====
  document.addEventListener('keydown', (e) => {
    // ESC to close mobile menu
    if (e.key === 'Escape') {
      const navbar = document.querySelector('#navbar');
      if (navbar && navbar.classList.contains('show')) {
        navbar.classList.remove('show');
        document.body.classList.remove('no-scroll');
      }
    }
  });

  // ===== RIPPLE EFFECT CSS =====
  const rippleStyle = document.createElement('style');
  rippleStyle.textContent = `
    .ripple {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.6);
      transform: scale(0);
      animation: rippleEffect 0.6s ease-out;
      pointer-events: none;
    }

    @keyframes rippleEffect {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(rippleStyle);

  console.log('✨ Premium animations loaded successfully!');
});

// ===== UTILITY FUNCTIONS =====
window.debounce = function(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

window.throttle = function(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};
