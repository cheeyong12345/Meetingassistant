/**
 * ============================================
 * MEETING ASSISTANT - UI ENHANCEMENTS
 * Interactive behaviors and micro-interactions
 * ============================================
 */

(function() {
  'use strict';

  /**
   * ============================================
   * 1. TOAST NOTIFICATION SYSTEM
   * ============================================
   */

  class ToastManager {
    constructor() {
      this.container = this.createContainer();
      document.body.appendChild(this.container);
    }

    createContainer() {
      const container = document.createElement('div');
      container.className = 'toast-container';
      container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1070;
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-width: 400px;
      `;
      return container;
    }

    show(message, type = 'info', duration = 5000) {
      const toast = this.createToast(message, type);
      this.container.appendChild(toast);

      // Trigger animation
      setTimeout(() => toast.classList.add('show'), 10);

      // Auto remove
      setTimeout(() => {
        this.remove(toast);
      }, duration);

      return toast;
    }

    createToast(message, type) {
      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;

      const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
      };

      toast.innerHTML = `
        <div class="alert-icon">${icons[type] || icons.info}</div>
        <div class="alert-content">${message}</div>
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
      `;

      return toast;
    }

    remove(toast) {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }
  }

  // Initialize toast manager
  window.toast = new ToastManager();

  /**
   * ============================================
   * 2. MODAL SYSTEM
   * ============================================
   */

  class ModalManager {
    constructor() {
      this.activeModals = [];
      this.init();
    }

    init() {
      // Close modal on overlay click
      document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
          this.close(e.target.querySelector('.modal'));
        }
      });

      // Close modal on ESC key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.activeModals.length > 0) {
          this.close(this.activeModals[this.activeModals.length - 1]);
        }
      });
    }

    open(modalId) {
      const modal = document.getElementById(modalId);
      if (!modal) return;

      const overlay = modal.closest('.modal-overlay') || this.createOverlay(modal);
      overlay.style.display = 'flex';
      document.body.style.overflow = 'hidden';

      this.activeModals.push(modal);

      // Focus trap
      this.trapFocus(modal);
    }

    close(modal) {
      if (!modal) return;

      const overlay = modal.closest('.modal-overlay');
      if (overlay) {
        overlay.style.display = 'none';
      }

      this.activeModals = this.activeModals.filter(m => m !== modal);

      if (this.activeModals.length === 0) {
        document.body.style.overflow = '';
      }
    }

    createOverlay(modal) {
      const overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      modal.parentNode.insertBefore(overlay, modal);
      overlay.appendChild(modal);
      return overlay;
    }

    trapFocus(modal) {
      const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstFocusable = focusableElements[0];
      const lastFocusable = focusableElements[focusableElements.length - 1];

      modal.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
          if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
              e.preventDefault();
              lastFocusable.focus();
            }
          } else {
            if (document.activeElement === lastFocusable) {
              e.preventDefault();
              firstFocusable.focus();
            }
          }
        }
      });

      firstFocusable?.focus();
    }
  }

  window.modal = new ModalManager();

  /**
   * ============================================
   * 3. RECORDING WAVEFORM ANIMATION
   * ============================================
   */

  class WaveformAnimation {
    constructor(container) {
      this.container = container;
      this.bars = [];
      this.isAnimating = false;
    }

    create(barCount = 5) {
      this.container.innerHTML = '';
      this.container.className = 'waveform-container';

      for (let i = 0; i < barCount; i++) {
        const bar = document.createElement('div');
        bar.className = 'waveform-bar';
        bar.style.cssText = `
          width: 4px;
          background: var(--color-primary-600);
          border-radius: 9999px;
          transition: height 0.1s ease;
        `;
        this.container.appendChild(bar);
        this.bars.push(bar);
      }
    }

    start() {
      this.isAnimating = true;
      this.animate();
    }

    stop() {
      this.isAnimating = false;
      this.bars.forEach(bar => {
        bar.style.height = '8px';
      });
    }

    animate() {
      if (!this.isAnimating) return;

      this.bars.forEach((bar, index) => {
        setTimeout(() => {
          const height = Math.random() * 32 + 8;
          bar.style.height = `${height}px`;
        }, index * 100);
      });

      setTimeout(() => this.animate(), 600);
    }
  }

  window.WaveformAnimation = WaveformAnimation;

  /**
   * ============================================
   * 4. TYPING EFFECT
   * ============================================
   */

  class TypingEffect {
    constructor(element, text, speed = 50) {
      this.element = element;
      this.text = text;
      this.speed = speed;
      this.index = 0;
    }

    start() {
      this.element.textContent = '';
      this.type();
    }

    type() {
      if (this.index < this.text.length) {
        this.element.textContent += this.text.charAt(this.index);
        this.index++;
        setTimeout(() => this.type(), this.speed);
      }
    }
  }

  window.TypingEffect = TypingEffect;

  /**
   * ============================================
   * 5. SMOOTH SCROLL
   * ============================================
   */

  function smoothScroll(target, duration = 500) {
    const targetElement = typeof target === 'string'
      ? document.querySelector(target)
      : target;

    if (!targetElement) return;

    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    function animation(currentTime) {
      if (startTime === null) startTime = currentTime;
      const timeElapsed = currentTime - startTime;
      const progress = Math.min(timeElapsed / duration, 1);

      // Easing function
      const ease = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;

      window.scrollTo(0, startPosition + distance * ease);

      if (timeElapsed < duration) {
        requestAnimationFrame(animation);
      }
    }

    requestAnimationFrame(animation);
  }

  window.smoothScroll = smoothScroll;

  /**
   * ============================================
   * 6. COPY TO CLIPBOARD WITH FEEDBACK
   * ============================================
   */

  async function copyToClipboard(text, button) {
    try {
      await navigator.clipboard.writeText(text);

      // Visual feedback
      if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '✓ Copied!';
        button.classList.add('btn-success');

        setTimeout(() => {
          button.innerHTML = originalText;
          button.classList.remove('btn-success');
        }, 2000);
      }

      toast.show('Copied to clipboard!', 'success', 2000);
      return true;
    } catch (error) {
      console.error('Failed to copy:', error);
      toast.show('Failed to copy to clipboard', 'error');
      return false;
    }
  }

  window.copyToClipboard = copyToClipboard;

  /**
   * ============================================
   * 7. FILE DRAG & DROP
   * ============================================
   */

  function initFileDragDrop(dropZone, fileInput, onFile) {
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('dragover');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0 && onFile) {
        onFile(files[0]);
      }
    }, false);

    // Click to upload
    dropZone.addEventListener('click', () => {
      fileInput?.click();
    });
  }

  window.initFileDragDrop = initFileDragDrop;

  /**
   * ============================================
   * 8. COUNTDOWN TIMER
   * ============================================
   */

  class CountdownTimer {
    constructor(element, startTime) {
      this.element = element;
      this.startTime = startTime || Date.now();
      this.interval = null;
    }

    start() {
      this.update();
      this.interval = setInterval(() => this.update(), 1000);
    }

    stop() {
      if (this.interval) {
        clearInterval(this.interval);
        this.interval = null;
      }
    }

    update() {
      const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
      const hours = Math.floor(elapsed / 3600);
      const minutes = Math.floor((elapsed % 3600) / 60);
      const seconds = elapsed % 60;

      const format = hours > 0
        ? `${hours}:${pad(minutes)}:${pad(seconds)}`
        : `${minutes}:${pad(seconds)}`;

      this.element.textContent = format;
    }
  }

  function pad(num) {
    return num.toString().padStart(2, '0');
  }

  window.CountdownTimer = CountdownTimer;

  /**
   * ============================================
   * 9. PROGRESS ANIMATION
   * ============================================
   */

  function animateProgress(progressBar, targetPercent, duration = 1000) {
    const start = parseFloat(progressBar.style.width) || 0;
    const change = targetPercent - start;
    const startTime = Date.now();

    function animate() {
      const currentTime = Date.now();
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const ease = progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;

      const currentPercent = start + change * ease;
      progressBar.style.width = `${currentPercent}%`;

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    }

    requestAnimationFrame(animate);
  }

  window.animateProgress = animateProgress;

  /**
   * ============================================
   * 10. SKELETON LOADER
   * ============================================
   */

  function showSkeleton(container, config = {}) {
    const {
      lines = 3,
      avatar = false,
      heading = false
    } = config;

    container.innerHTML = '';
    container.classList.add('skeleton-container');

    if (avatar) {
      const avatarEl = document.createElement('div');
      avatarEl.className = 'skeleton skeleton-avatar';
      container.appendChild(avatarEl);
    }

    if (heading) {
      const headingEl = document.createElement('div');
      headingEl.className = 'skeleton skeleton-heading';
      container.appendChild(headingEl);
    }

    for (let i = 0; i < lines; i++) {
      const line = document.createElement('div');
      line.className = 'skeleton skeleton-text';
      if (i === lines - 1) {
        line.style.width = '70%';
      }
      container.appendChild(line);
    }
  }

  function hideSkeleton(container, content) {
    container.classList.remove('skeleton-container');
    container.innerHTML = content;
  }

  window.showSkeleton = showSkeleton;
  window.hideSkeleton = hideSkeleton;

  /**
   * ============================================
   * 11. INFINITE SCROLL
   * ============================================
   */

  function initInfiniteScroll(container, loadMore, threshold = 200) {
    let isLoading = false;

    container.addEventListener('scroll', () => {
      if (isLoading) return;

      const scrollPosition = container.scrollTop + container.clientHeight;
      const scrollHeight = container.scrollHeight;

      if (scrollPosition >= scrollHeight - threshold) {
        isLoading = true;
        loadMore().finally(() => {
          isLoading = false;
        });
      }
    });
  }

  window.initInfiniteScroll = initInfiniteScroll;

  /**
   * ============================================
   * 12. AUTO-SAVE INDICATOR
   * ============================================
   */

  class AutoSaveIndicator {
    constructor(element) {
      this.element = element;
      this.timeout = null;
    }

    saving() {
      clearTimeout(this.timeout);
      this.element.innerHTML = '💾 Saving...';
      this.element.className = 'badge badge-warning';
    }

    saved() {
      this.element.innerHTML = '✓ Saved';
      this.element.className = 'badge badge-success';

      this.timeout = setTimeout(() => {
        this.element.innerHTML = '';
      }, 3000);
    }

    error() {
      this.element.innerHTML = '✕ Error';
      this.element.className = 'badge badge-error';

      this.timeout = setTimeout(() => {
        this.element.innerHTML = '';
      }, 5000);
    }
  }

  window.AutoSaveIndicator = AutoSaveIndicator;

  /**
   * ============================================
   * 13. DEBOUNCE & THROTTLE UTILITIES
   * ============================================
   */

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  window.debounce = debounce;
  window.throttle = throttle;

  /**
   * ============================================
   * 14. RIPPLE EFFECT
   * ============================================
   */

  function createRipple(event) {
    const button = event.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
    circle.classList.add('ripple');

    const ripple = button.getElementsByClassName('ripple')[0];
    if (ripple) {
      ripple.remove();
    }

    button.appendChild(circle);
  }

  // Auto-apply to buttons
  document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.btn:not(.btn-ghost)');
    buttons.forEach(button => {
      button.addEventListener('click', createRipple);
    });
  });

  /**
   * ============================================
   * 15. FORM VALIDATION HELPERS
   * ============================================
   */

  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  function showFieldError(field, message) {
    field.classList.add('error');

    let errorEl = field.nextElementSibling;
    if (!errorEl || !errorEl.classList.contains('form-error')) {
      errorEl = document.createElement('div');
      errorEl.className = 'form-error';
      field.parentNode.insertBefore(errorEl, field.nextSibling);
    }

    errorEl.textContent = message;
  }

  function clearFieldError(field) {
    field.classList.remove('error');

    const errorEl = field.nextElementSibling;
    if (errorEl && errorEl.classList.contains('form-error')) {
      errorEl.remove();
    }
  }

  window.validateEmail = validateEmail;
  window.showFieldError = showFieldError;
  window.clearFieldError = clearFieldError;

  /**
   * ============================================
   * 16. INITIALIZE ON DOM READY
   * ============================================
   */

  document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scroll to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          smoothScroll(target);
        }
      });
    });

    // Auto-hide alerts
    document.querySelectorAll('.alert').forEach(alert => {
      setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }, 5000);
    });

    console.log('UI Enhancements loaded successfully!');
  });

})();
