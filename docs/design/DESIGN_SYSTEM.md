# Meeting Assistant - Design System Specification

## Table of Contents
1. [Introduction](#introduction)
2. [Design Tokens](#design-tokens)
3. [Component Specifications](#component-specifications)
4. [Usage Guidelines](#usage-guidelines)
5. [Implementation Notes](#implementation-notes)

---

## Introduction

This design system provides a comprehensive, scalable foundation for the Meeting Assistant application. It follows modern design principles, ensures accessibility compliance (WCAG 2.1 AA), and maintains consistency across all interfaces.

### Design System Goals
- **Consistency**: Unified visual language across all components
- **Scalability**: Easy to extend and maintain
- **Accessibility**: WCAG 2.1 AA compliant by default
- **Performance**: Optimized for 60fps animations
- **Developer-Friendly**: Clear documentation and easy implementation

---

## Design Tokens

Design tokens are the atomic building blocks of our design system. They're implemented as CSS custom properties for easy theming and consistency.

### Color Tokens

#### Primary Colors
```css
--color-primary: #6366F1          /* Indigo - Main brand color */
--color-primary-hover: #4F46E5    /* Darker for hover states */
--color-primary-light: #EEF2FF    /* Light backgrounds */
--color-primary-dark: #3730A3     /* Darker accents */
```

**Usage:**
- Primary buttons
- Links
- Active states
- Brand elements

**Accessibility:**
- White on Primary: 5.2:1 (AA compliant)
- Primary on White: 8.5:1 (AAA compliant)

#### Secondary Colors
```css
--color-secondary: #8B5CF6        /* Purple - Supporting brand color */
--color-secondary-hover: #7C3AED
--color-secondary-light: #F5F3FF
```

**Usage:**
- Secondary buttons
- Accent elements
- Alternative CTAs

#### Semantic Colors

**Success (Green)**
```css
--color-success: #10B981
--color-success-hover: #059669
--color-success-light: #D1FAE5
--color-success-dark: #047857
```
- Recording indicators
- Success messages
- Completed states
- Positive metrics

**Warning (Amber)**
```css
--color-warning: #F59E0B
--color-warning-hover: #D97706
--color-warning-light: #FEF3C7
--color-warning-dark: #B45309
```
- Processing states
- Attention needed
- Warnings

**Error (Red)**
```css
--color-error: #EF4444
--color-error-hover: #DC2626
--color-error-light: #FEE2E2
--color-error-dark: #B91C1C
```
- Error messages
- Stop buttons
- Failed states
- Destructive actions

**Info (Blue)**
```css
--color-info: #3B82F6
--color-info-hover: #2563EB
--color-info-light: #DBEAFE
--color-info-dark: #1D4ED8
```
- Information messages
- Help tooltips
- Neutral status

#### Neutral Palette

```css
--color-gray-50: #F9FAFB    /* Lightest - Page backgrounds */
--color-gray-100: #F3F4F6   /* Light backgrounds */
--color-gray-200: #E5E7EB   /* Borders, dividers */
--color-gray-300: #D1D5DB   /* Disabled borders */
--color-gray-400: #9CA3AF   /* Placeholder text */
--color-gray-500: #6B7280   /* Secondary text */
--color-gray-600: #4B5563   /* Body text */
--color-gray-700: #374151   /* Headings, labels */
--color-gray-800: #1F2937   /* Dark backgrounds */
--color-gray-900: #111827   /* Primary text */
```

**Contrast Ratios:**
- Gray-900 on White: 16.1:1 (AAA)
- Gray-600 on White: 7.3:1 (AAA)
- Gray-500 on White: 4.6:1 (AA)

### Typography Tokens

#### Font Families
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', monospace;
--font-display: 'Cal Sans', 'Inter', sans-serif;
```

**Fallback Strategy:**
- System fonts ensure fast loading
- Web fonts loaded with `font-display: swap`
- Monospace for code and transcripts

#### Font Sizes (Type Scale 1.250)
```css
--text-xs: 0.75rem      /* 12px - Captions, timestamps */
--text-sm: 0.875rem     /* 14px - Small text, labels */
--text-base: 1rem       /* 16px - Body text (base) */
--text-lg: 1.125rem     /* 18px - Large body, lead */
--text-xl: 1.25rem      /* 20px - Small headings */
--text-2xl: 1.5rem      /* 24px - Headings */
--text-3xl: 1.875rem    /* 30px - Large headings */
--text-4xl: 2.25rem     /* 36px - Page titles */
--text-5xl: 3rem        /* 48px - Hero text */
```

**Usage Guidelines:**
- Never go below 14px for body text (accessibility)
- Use relative units (rem) for scalability
- Maintain hierarchy with size + weight

#### Font Weights
```css
--font-normal: 400      /* Body text */
--font-medium: 500      /* Emphasis, labels */
--font-semibold: 600    /* Headings, buttons */
--font-bold: 700        /* Strong emphasis */
```

#### Line Heights
```css
--leading-none: 1           /* Tight headings */
--leading-tight: 1.25       /* Headings */
--leading-snug: 1.375       /* Subheadings */
--leading-normal: 1.5       /* Body text */
--leading-relaxed: 1.625    /* Loose body */
--leading-loose: 2          /* Spacious text */
```

### Spacing Tokens (8px Base Grid)

```css
--space-0: 0
--space-1: 0.25rem     /* 4px - Icon gaps */
--space-2: 0.5rem      /* 8px - Base unit */
--space-3: 0.75rem     /* 12px - Compact padding */
--space-4: 1rem        /* 16px - Standard spacing */
--space-5: 1.25rem     /* 20px */
--space-6: 1.5rem      /* 24px - Card padding */
--space-8: 2rem        /* 32px - Section spacing */
--space-10: 2.5rem     /* 40px */
--space-12: 3rem       /* 48px - Large gaps */
--space-16: 4rem       /* 64px - Major sections */
--space-20: 5rem       /* 80px */
--space-24: 6rem       /* 96px - Hero spacing */
```

**8px Grid System:**
- All spacing multiples of 4 or 8
- Ensures visual consistency
- Aligns with common screen densities

### Border Radius Tokens

```css
--radius-none: 0
--radius-sm: 0.25rem     /* 4px - Subtle rounding */
--radius-base: 0.5rem    /* 8px - Default */
--radius-md: 0.75rem     /* 12px - Cards, inputs */
--radius-lg: 1rem        /* 16px - Large cards */
--radius-xl: 1.5rem      /* 24px - Feature cards */
--radius-2xl: 2rem       /* 32px - Hero elements */
--radius-full: 9999px    /* Circles, pills */
```

### Shadow Tokens

```css
/* Elevation System */
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1),
             0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-base: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
               0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
--shadow-2xl: 0 35px 60px -15px rgba(0, 0, 0, 0.3);
--shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
```

**Elevation Levels:**
- xs: Subtle depth (table rows)
- sm: Default cards
- base: Hovered cards
- md: Dropdowns, popovers
- lg: Modals, dialogs
- xl: Large modals
- 2xl: Special features

### Animation Tokens

#### Duration
```css
--duration-fast: 150ms     /* Micro-interactions */
--duration-base: 250ms     /* Standard transitions */
--duration-slow: 350ms     /* Complex animations */
--duration-slower: 500ms   /* Page transitions */
```

#### Easing Functions
```css
--ease-in: cubic-bezier(0.4, 0, 1, 1)              /* Accelerating */
--ease-out: cubic-bezier(0, 0, 0.2, 1)             /* Decelerating */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)        /* Standard */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1)   /* Bouncy */
```

**Usage Guidelines:**
- ease-out: Most common (UI element appearing)
- ease-in: Element disappearing
- ease-in-out: Element changing state
- ease-spring: Playful, attention-grabbing

---

## Component Specifications

### Buttons

#### Primary Button
```css
Component: .btn.btn-primary
Background: var(--color-primary)
Color: white
Padding: var(--space-3) var(--space-6)
Border-radius: var(--radius-md)
Font-weight: var(--font-semibold)
Shadow: var(--shadow-sm)
```

**States:**
```css
Hover:
  - Background → var(--color-primary-hover)
  - Shadow → var(--shadow-md)
  - Transform → translateY(-1px)

Active:
  - Transform → translateY(0)

Focus:
  - Outline → 2px solid var(--color-primary)
  - Outline-offset → 2px

Disabled:
  - Opacity → 0.5
  - Cursor → not-allowed
```

**Accessibility:**
- Minimum height: 44px (touch target)
- Focus indicator visible
- ARIA labels for icon-only buttons

#### Button Variants

**Secondary Button**
- Background: var(--color-gray-100)
- Color: var(--color-gray-700)
- Border: 2px solid var(--color-gray-200)

**Ghost Button**
- Background: Transparent
- Color: var(--color-gray-700)
- Border: 1px solid var(--color-gray-200)

**Danger Button**
- Background: var(--color-error)
- Color: white
- Used for destructive actions

**Icon Button**
- Padding: var(--space-2)
- Border-radius: var(--radius-full)
- Square aspect ratio

### Input Fields

#### Text Input
```css
Component: .form-input
Border: 2px solid var(--color-gray-200)
Border-radius: var(--radius-md)
Padding: var(--space-3) var(--space-4)
Font-size: var(--text-base)
Color: var(--color-gray-900)
Background: white
```

**States:**
```css
Focus:
  - Border-color → var(--color-primary)
  - Box-shadow → 0 0 0 3px rgba(99, 102, 241, 0.1)

Error:
  - Border-color → var(--color-error)
  - Color → var(--color-error)

Disabled:
  - Background → var(--color-gray-100)
  - Opacity → 0.6
  - Cursor → not-allowed
```

**Accessibility:**
- Labels always visible (no placeholders as labels)
- Error messages programmatically associated
- Minimum height: 44px

#### Select Dropdown
- Same styling as text input
- Chevron icon on right
- Custom styling for consistent appearance

#### Textarea
- Same styling as text input
- Min-height: 120px
- Resize: vertical only
- Font-family: var(--font-mono) for code/transcripts

### Cards

#### Standard Card
```css
Component: .card
Background: white
Border: 1px solid var(--color-gray-200)
Border-radius: var(--radius-lg)
Padding: var(--space-6)
Shadow: var(--shadow-sm)
```

**Structure:**
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">
    Content
  </div>
  <div class="card-footer">
    Actions
  </div>
</div>
```

**Variants:**
- Elevated: Higher shadow, no border
- Glass: Transparent background, backdrop blur
- Sticky: Position sticky for sidebar cards

### Status Indicators

#### Recording Indicator
```css
Component: .recording-indicator
Display: inline-flex
Gap: var(--space-2)
Padding: var(--space-2) var(--space-4)
Background: rgba(239, 68, 68, 0.1)
Border: 2px solid var(--color-error)
Border-radius: var(--radius-full)
Color: var(--color-error)
Animation: pulse-recording 1.5s infinite
```

**Animation:**
```css
@keyframes pulse-recording {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}
```

#### Connection Status Dot
```css
Component: .status-indicator
Size: 10px × 10px
Border-radius: var(--radius-full)

States:
  - Online: var(--color-success) + pulse animation
  - Offline: var(--color-error)
  - Connecting: var(--color-warning) + pulse animation
```

### Badges

```css
Component: .badge
Display: inline-flex
Padding: var(--space-1) var(--space-3)
Font-size: var(--text-xs)
Font-weight: var(--font-medium)
Border-radius: var(--radius-full)
Line-height: 1
```

**Variants:**
- Primary: Blue background
- Success: Green background
- Warning: Amber background
- Error: Red background
- Secondary: Gray background

### Alerts & Notifications

#### Alert Box
```css
Component: .alert
Padding: var(--space-4)
Border-radius: var(--radius-md)
Border-left: 4px solid
Display: flex
Gap: var(--space-3)
Animation: slideInDown 250ms
```

**Variants:**
- Success: Green border, light green background
- Error: Red border, light red background
- Warning: Amber border, light amber background
- Info: Blue border, light blue background

#### Toast Notification
```css
Component: .toast
Position: Fixed (top-right)
Background: white
Shadow: var(--shadow-xl)
Border-radius: var(--radius-xl)
Padding: var(--space-4)
Animation: slideInRight 250ms
Auto-dismiss: 5 seconds (success) / Manual (errors)
```

### Progress Indicators

#### Linear Progress Bar
```css
Component: .progress
Height: 8px
Background: var(--color-gray-200)
Border-radius: var(--radius-full)

.progress-bar:
  - Background: Linear gradient (primary colors)
  - Transition: width 250ms
  - Animated shimmer effect
```

#### Spinner (Loading)
```css
Component: .spinner
Size: 24px (small), 40px (default), 64px (large)
Border: 3px solid var(--color-gray-200)
Border-top-color: var(--color-primary)
Border-radius: var(--radius-full)
Animation: spin 1s linear infinite
```

### Transcript Display

#### Transcript Container
```css
Component: .transcript-container
Background: var(--color-gray-50)
Border: 2px solid var(--color-gray-200)
Border-radius: var(--radius-xl)
Padding: var(--space-6)
Min-height: 300px
Max-height: 600px
Overflow-y: auto
Font-family: var(--font-mono)
```

**Scrollbar Styling:**
```css
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-gray-100);
}

::-webkit-scrollbar-thumb {
  background: var(--color-gray-400);
  border-radius: var(--radius-md);
}
```

#### Transcript Segment
```css
Component: .transcript-segment
Background: white
Padding: var(--space-4)
Border-radius: var(--radius-md)
Border-left: 3px solid var(--color-primary)
Animation: fadeIn 250ms
```

### Waveform Visualization

```css
Component: .waveform-container
Display: flex
Gap: 3px
Height: 48px
Align-items: center

.waveform-bar:
  - Width: 4px
  - Background: var(--color-primary)
  - Border-radius: var(--radius-full)
  - Animation: waveform 1.2s infinite
  - Staggered delays for wave effect
```

### Metric Cards

```css
Component: .metric-card
Background: white
Padding: var(--space-6)
Border-radius: var(--radius-xl)
Border: 2px solid var(--color-gray-200)

Structure:
  - Icon (40px, colored background)
  - Label (uppercase, small)
  - Value (large, bold)
```

---

## Usage Guidelines

### Color Usage

**Do's:**
- Use semantic colors for their intended purpose
- Maintain sufficient contrast (4.5:1 for text)
- Use primary color for primary actions
- Use neutral colors for most UI elements

**Don'ts:**
- Don't use color as the only indicator
- Don't use too many colors at once
- Don't override semantic colors for other purposes

### Typography Usage

**Hierarchy:**
1. Page Title (h1): --text-4xl, bold
2. Section Heading (h2): --text-3xl, bold
3. Subsection (h3): --text-2xl, semibold
4. Card Title (h4): --text-xl, semibold
5. Body Text: --text-base, normal
6. Secondary Text: --text-sm, normal
7. Captions: --text-xs, medium

**Best Practices:**
- Never use font sizes smaller than 14px
- Maintain consistent line-height within sections
- Use font-weight to create emphasis, not just size
- Limit font families (primary + mono only)

### Spacing Usage

**Consistent Rhythm:**
- Component padding: --space-6 (24px)
- Element gaps: --space-4 (16px)
- Section margins: --space-12 (48px)
- Icon gaps: --space-2 (8px)

**Responsive Spacing:**
- Reduce spacing on mobile (50-75% of desktop)
- Maintain visual hierarchy at all sizes

### Animation Usage

**Performance Rules:**
- Only animate `transform` and `opacity`
- Use `will-change` sparingly
- Never animate `width`, `height`, or `background-color`
- Respect `prefers-reduced-motion`

**Best Practices:**
- Micro-interactions: 150ms
- State changes: 250ms
- Page transitions: 350ms
- Keep animations subtle and purposeful

---

## Implementation Notes

### CSS Variable Organization

```css
:root {
  /* 1. Color Tokens */
  /* 2. Typography Tokens */
  /* 3. Spacing Tokens */
  /* 4. Border Radius Tokens */
  /* 5. Shadow Tokens */
  /* 6. Animation Tokens */
  /* 7. Z-index Tokens */
}
```

### Component Naming Convention

**BEM Methodology:**
```css
.block { }                    /* Component */
.block__element { }           /* Child element */
.block--modifier { }          /* Variation */
.block__element--modifier { } /* Element variation */
```

**Examples:**
```css
.card { }
.card__header { }
.card__body { }
.card--elevated { }
```

### Utility Classes

```css
/* Spacing */
.mt-{n}, .mb-{n}, .ml-{n}, .mr-{n}
.p-{n}, .pt-{n}, .pb-{n}, .pl-{n}, .pr-{n}

/* Flexbox */
.flex, .flex-col, .items-center, .justify-between, .gap-{n}

/* Text */
.text-center, .text-left, .text-right
.text-{size}
.font-{weight}

/* Display */
.hidden, .visible, .block, .inline-block
```

### Responsive Breakpoints

```css
/* Mobile First Approach */
/* Default: Mobile (< 640px) */

@media (min-width: 640px) {
  /* Tablet */
}

@media (min-width: 1024px) {
  /* Desktop */
}

@media (min-width: 1280px) {
  /* Large Desktop */
}
```

### Dark Mode (Future)

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: var(--color-gray-900);
    --color-text: var(--color-gray-50);
    /* Override tokens for dark mode */
  }
}
```

### Browser Support

**Target Browsers:**
- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)

**Progressive Enhancement:**
- CSS Grid with flexbox fallback
- CSS Variables with fallback values
- Modern features with @supports

### Performance Checklist

- [ ] Use CSS containment for large lists
- [ ] Implement intersection observer for lazy loading
- [ ] Use transform for animations (GPU accelerated)
- [ ] Minimize repaints and reflows
- [ ] Critical CSS inlined in `<head>`
- [ ] Non-critical CSS loaded async

---

## Component Checklist

When creating a new component, ensure:

- [ ] Uses design tokens (no hardcoded values)
- [ ] Responsive at all breakpoints
- [ ] Accessible (WCAG 2.1 AA)
- [ ] Keyboard navigable
- [ ] Focus states visible
- [ ] ARIA labels when needed
- [ ] Respects reduced motion preference
- [ ] Documented in this design system
- [ ] Tested across browsers
- [ ] Performance optimized

---

## Maintenance

### Version History
- v1.0.0 (2025-10-01): Initial design system

### Change Management
- All changes require design review
- Breaking changes require major version bump
- New components added with documentation
- Deprecated components marked for removal

### Contributing
1. Follow existing patterns
2. Document new tokens/components
3. Ensure accessibility compliance
4. Test across browsers
5. Update this specification

---

## Resources

### Tools
- Figma: Design mockups
- Chrome DevTools: Accessibility audit
- WAVE: Accessibility testing
- Lighthouse: Performance testing

### References
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Inter Font](https://rsms.me/inter/)
- [Material Design Motion](https://material.io/design/motion)
- [Inclusive Components](https://inclusive-components.design/)

---

## Conclusion

This design system provides a robust foundation for building consistent, accessible, and performant UI components. By following these specifications, developers can create interfaces that not only look great but also provide an excellent user experience for all users.

Remember: **Design systems are living documents**. As the application evolves, so should this specification. Regular audits and updates ensure the design system remains relevant and useful.
