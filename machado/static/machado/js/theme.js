/**
 * MACHADO — Theme Controller
 * Handles the accent color picker and persists state to localStorage.
 */

document.addEventListener('DOMContentLoaded', function () {

  var accentKey = 'machado-accent' + (window.MACHADO_URL_PREFIX || '');

  // --- Accent Picker Toggle ---
  var accentPicker = document.getElementById('accent-picker');
  if (accentPicker) {
    var accentBtn = accentPicker.querySelector('.m-theme-btn');
    if (accentBtn) {
      accentBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        accentPicker.classList.toggle('open');
      });
    }

    // Close picker when clicking outside
    document.addEventListener('click', function (e) {
      if (!accentPicker.contains(e.target)) {
        accentPicker.classList.remove('open');
      }
    });
  }

  // --- Accent Swatches ---
  var swatches = document.querySelectorAll('[data-set-accent]');
  swatches.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var accent = this.getAttribute('data-set-accent');
      document.documentElement.setAttribute('data-accent', accent);
      localStorage.setItem(accentKey, accent);

      // Update active state
      swatches.forEach(function (b) { b.classList.remove('active'); });
      this.classList.add('active');
    });
  });

  // Mark current accent as active
  var currentAccent = document.documentElement.getAttribute('data-accent') || 'steel';
  var activeBtn = document.querySelector('[data-set-accent="' + currentAccent + '"]');
  if (activeBtn) activeBtn.classList.add('active');

  // --- Scroll Entrance Animations ---
  var animatedElements = document.querySelectorAll('.m-fade-up');
  if (animatedElements.length > 0) {
    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      animatedElements.forEach(function (el) {
        el.classList.add('visible');
      });
    } else {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      });

      animatedElements.forEach(function (el) {
        observer.observe(el);
      });
    }
  }

});
