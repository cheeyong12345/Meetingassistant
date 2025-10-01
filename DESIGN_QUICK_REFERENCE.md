# Meeting Assistant - Design System Quick Reference

Quick cheat sheet for common components and utilities.

---

## 🎨 Colors

```css
/* Text Colors */
.text-primary      /* Purple */
.text-success      /* Green */
.text-warning      /* Amber */
.text-error        /* Red */
.text-gray         /* Gray */

/* Background Colors */
.bg-primary        /* Purple background */
.bg-success        /* Green background */
.bg-white          /* White */
.bg-gray           /* Light gray */
```

---

## 🔘 Buttons

```html
<!-- Primary Action -->
<button class="btn btn-primary">Action</button>

<!-- Secondary Action -->
<button class="btn btn-secondary">Secondary</button>

<!-- Success -->
<button class="btn btn-success">Success</button>

<!-- Danger -->
<button class="btn btn-danger">Delete</button>

<!-- Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary btn-lg">Large</button>
<button class="btn btn-primary btn-block">Full Width</button>

<!-- Variants -->
<button class="btn btn-outline">Outline</button>
<button class="btn btn-ghost">Ghost</button>

<!-- Icon Button -->
<button class="btn btn-icon btn-primary">🔍</button>
```

---

## 📦 Cards

```html
<!-- Basic Card -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">
    Content
  </div>
  <div class="card-footer">
    Footer
  </div>
</div>

<!-- Gradient Card -->
<div class="card card-gradient">
  <!-- Content -->
</div>

<!-- Glass Card -->
<div class="card card-glass">
  <!-- Content -->
</div>

<!-- Metric Card -->
<div class="metric-card">
  <div class="metric-label">Duration</div>
  <div class="metric-value">12:34</div>
  <div class="metric-change positive">+15%</div>
</div>
```

---

## 📝 Forms

```html
<!-- Input Field -->
<div class="form-group">
  <label class="form-label" for="name">Name</label>
  <input type="text" class="form-input" id="name" placeholder="Enter name">
  <span class="form-hint">Helper text</span>
</div>

<!-- Textarea -->
<div class="form-group">
  <label class="form-label">Description</label>
  <textarea class="form-textarea"></textarea>
</div>

<!-- Toggle Switch -->
<div class="toggle">
  <input type="checkbox" id="toggle1">
  <span class="toggle-slider"></span>
</div>

<!-- Checkbox -->
<label class="checkbox">
  <input type="checkbox">
  <span>Accept terms</span>
</label>

<!-- Radio -->
<label class="radio">
  <input type="radio" name="option">
  <span>Option 1</span>
</label>
```

---

## 🏷️ Badges

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-error">Error</span>
<span class="badge badge-lg">Large Badge</span>

<!-- Status Dot -->
<span class="status-dot online"></span> Online
<span class="status-dot offline"></span> Offline
<span class="status-dot busy"></span> Busy
```

---

## 📊 Progress

```html
<!-- Progress Bar -->
<div class="progress">
  <div class="progress-bar" style="width: 75%"></div>
</div>

<!-- Sizes -->
<div class="progress progress-sm">...</div>
<div class="progress progress-lg">...</div>
```

---

## 🚨 Alerts

```html
<div class="alert alert-success">
  <div class="alert-icon">✓</div>
  <div class="alert-content">
    <div class="alert-title">Success!</div>
    Operation completed successfully.
  </div>
  <button class="alert-close">×</button>
</div>

<!-- Types: alert-success, alert-warning, alert-error, alert-info -->
```

---

## 🪟 Modals

```html
<div class="modal-overlay" style="display: none;">
  <div class="modal">
    <div class="modal-header">
      <h2 class="modal-title">Modal Title</h2>
      <button class="modal-close">×</button>
    </div>
    <div class="modal-body">
      Content
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost">Cancel</button>
      <button class="btn btn-primary">Confirm</button>
    </div>
  </div>
</div>

<!-- JavaScript -->
<script>
modal.open('modal-id');
modal.close(modalElement);
</script>
```

---

## 🔄 Loading

```html
<!-- Spinner -->
<div class="spinner"></div>
<div class="spinner spinner-lg"></div>

<!-- Skeleton -->
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-heading"></div>
<div class="skeleton skeleton-avatar"></div>
```

---

## 🎭 Animations

```html
<!-- Entrance -->
<div class="fade-in">Fade in</div>
<div class="fade-in-up">Fade in from bottom</div>
<div class="scale-in">Scale in</div>
<div class="slide-in-up">Slide up</div>

<!-- Continuous -->
<div class="pulse">Pulse</div>
<div class="spin">Spin</div>
<div class="bounce">Bounce</div>
<div class="float">Float</div>

<!-- Hover Effects -->
<div class="lift-hover">Lifts on hover</div>
<div class="grow-hover">Grows on hover</div>
<div class="shine-hover">Shines on hover</div>

<!-- Staggered -->
<div class="stagger-fade-in">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- Delays & Durations -->
<div class="fade-in delay-200">Delayed</div>
<div class="fade-in duration-slow">Slow</div>
```

---

## 📐 Layout

```html
<!-- Container -->
<div class="container">
  <!-- Max-width content -->
</div>

<!-- Grid -->
<div class="grid grid-cols-3 gap-4">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>

<!-- Responsive Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- Responsive columns -->
</div>

<!-- Flexbox -->
<div class="flex items-center justify-between gap-4">
  <div>Left</div>
  <div>Right</div>
</div>
```

---

## 📏 Spacing

```html
<!-- Margin -->
<div class="mt-4">Margin top</div>
<div class="mb-6">Margin bottom</div>
<div class="m-4">All margins</div>

<!-- Padding -->
<div class="p-4">Padding</div>
<div class="p-0">No padding</div>

<!-- Gap -->
<div class="flex gap-4">With gap</div>

/* Values: 0, 1 (4px), 2 (8px), 3 (12px), 4 (16px), 6 (24px), 8 (32px) */
```

---

## 🎯 JavaScript Utilities

```javascript
// Toast Notifications
toast.show('Message here', 'success', 5000);
// Types: success, error, warning, info

// Modal
modal.open('modal-id');
modal.close(modalElement);

// Copy to Clipboard
await copyToClipboard('Text to copy', buttonElement);

// Progress
animateProgress(progressBar, 75, 1000);

// Waveform
const waveform = new WaveformAnimation(container);
waveform.create(5);
waveform.start();
waveform.stop();

// Typing Effect
new TypingEffect(element, 'Text to type', 50).start();

// Countdown Timer
const timer = new CountdownTimer(element, startTime);
timer.start();
timer.stop();

// Utilities
const debounced = debounce(func, 300);
const throttled = throttle(func, 100);
smoothScroll('#target', 500);
```

---

## 🎨 Design Tokens

```css
/* Most Common Colors */
--color-primary-600: #7c3aed
--color-success: #10b981
--color-error: #ef4444
--color-warning: #f59e0b

/* Font Sizes */
--text-sm: 0.875rem    /* 14px */
--text-base: 1rem      /* 16px */
--text-lg: 1.125rem    /* 18px */
--text-2xl: 1.5rem     /* 24px */

/* Spacing */
--space-2: 0.5rem      /* 8px */
--space-4: 1rem        /* 16px */
--space-6: 1.5rem      /* 24px */

/* Border Radius */
--radius-lg: 0.5rem    /* 8px */
--radius-xl: 0.75rem   /* 12px */
--radius-full: 9999px

/* Shadows */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)

/* Gradients */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
```

---

## 🔍 Common Patterns

### Hero Section
```html
<div class="hero" style="background: var(--gradient-primary); padding: 4rem 0; color: white;">
  <div class="container text-center">
    <h1 class="text-5xl mb-4">Welcome to Meeting Assistant</h1>
    <p class="text-xl mb-6">AI-powered meeting transcription</p>
    <button class="btn btn-lg" style="background: white; color: var(--color-primary-600);">
      Get Started
    </button>
  </div>
</div>
```

### Dashboard Metrics
```html
<div class="grid grid-cols-3 gap-4">
  <div class="metric-card">
    <div class="metric-label">Duration</div>
    <div class="metric-value">12:34</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Words</div>
    <div class="metric-value">1,234</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Speakers</div>
    <div class="metric-value">3</div>
  </div>
</div>
```

### Form with Validation
```html
<form>
  <div class="form-group">
    <label class="form-label form-label-required">Email</label>
    <input type="email" class="form-input" required>
    <span class="form-error" style="display: none;">Invalid email</span>
  </div>
  <button type="submit" class="btn btn-primary btn-block">Submit</button>
</form>
```

---

## ♿ Accessibility

```html
<!-- Always include -->
<button aria-label="Close modal">×</button>
<div role="status" aria-live="polite">Status message</div>
<input aria-describedby="help-text">
<span id="help-text" class="form-hint">Helper text</span>

<!-- Skip link -->
<a href="#main" class="skip-link">Skip to content</a>

<!-- Screen reader only -->
<span class="sr-only">Hidden but accessible text</span>
```

---

## 📱 Responsive

```html
<!-- Breakpoints: sm (640px), md (768px), lg (1024px) -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  <!-- 1 column mobile, 2 tablet, 4 desktop -->
</div>

<!-- Touch-friendly (44px minimum) -->
<button class="btn btn-lg">Large Button</button>
```

---

## 🚀 Quick Tips

1. **Always use design tokens** instead of hardcoded values
2. **Mobile-first** - Design for mobile, enhance for desktop
3. **Accessibility** - Include ARIA labels and semantic HTML
4. **Performance** - Use transforms & opacity for animations
5. **Consistency** - Stick to the component library
6. **Testing** - Check on multiple browsers and devices

---

## 📚 Full Documentation

For complete documentation, see:
- **VISUAL_DESIGN_GUIDE.md** - Complete implementation guide
- **DESIGN_SYSTEM_SUMMARY.md** - Detailed summary
- **Component Templates** - `/templates/components/`

---

**Version**: 2.0.0 | **Last Updated**: October 1, 2025
