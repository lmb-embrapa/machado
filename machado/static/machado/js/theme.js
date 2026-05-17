/**
 * MACHADO — Theme Controller
 * Handles the accent color picker and persists state to localStorage.
 */

document.addEventListener('DOMContentLoaded', function () {

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
      localStorage.setItem('machado-accent', accent);

      // Update active state
      swatches.forEach(function (b) { b.classList.remove('active'); });
      this.classList.add('active');
    });
  });

  // Mark current accent as active
  var currentAccent = document.documentElement.getAttribute('data-accent') || 'steel';
  var activeBtn = document.querySelector('[data-set-accent="' + currentAccent + '"]');
  if (activeBtn) activeBtn.classList.add('active');

});
