/**
 * Meeting Assistant - Demo Features
 * Special enhancements for impressive live demonstrations
 * @version 1.0.0
 */

/* =============================================================================
   Demo Mode Manager
   ============================================================================= */
class DemoMode {
  static enabled = false;
  static simulationInterval = null;

  static enable() {
    this.enabled = true;
    console.log('[Demo Mode] Enabled');
    NotificationManager.show('Demo mode enabled - simulated data active', 'info');
  }

  static disable() {
    this.enabled = false;
    this.stopSimulation();
    console.log('[Demo Mode] Disabled');
  }

  static toggle() {
    if (this.enabled) {
      this.disable();
    } else {
      this.enable();
    }
  }

  static startSimulation() {
    if (!this.enabled) return;

    this.stopSimulation();

    const demoTranscripts = [
      "Let's start today's standup. Who wants to go first?",
      "I completed the user authentication feature yesterday.",
      "I'm working on the database optimization today.",
      "No blockers on my end.",
      "I finished the API integration. It's ready for testing.",
      "Today I'll be refactoring the payment module.",
      "I'm blocked on the design review. Need feedback from Sarah.",
      "Completed code review for PR #123.",
      "Working on implementing the new dashboard layout.",
      "No issues to report. Everything is on track.",
      "I'll be pair programming with Mike this afternoon.",
      "Deployed the hotfix to production successfully.",
      "Need to schedule a meeting to discuss the architecture.",
      "Finished writing unit tests for the new feature.",
      "Starting work on the mobile responsive design."
    ];

    let index = 0;

    this.simulationInterval = setInterval(() => {
      if (AppState.isRecording && index < demoTranscripts.length) {
        const segment = {
          text: demoTranscripts[index],
          timestamp: new Date().toISOString()
        };

        TranscriptManager.addSegment(segment);
        index++;

        // Update metrics
        MetricsManager.update({
          wordCount: TranscriptManager.segments.length * 8
        });
      } else {
        this.stopSimulation();
      }
    }, 3000); // Every 3 seconds
  }

  static stopSimulation() {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
      this.simulationInterval = null;
    }
  }
}

/* =============================================================================
   Visual Effects for Demos
   ============================================================================= */
class DemoEffects {
  // Confetti effect for successful meeting completion
  static celebrateSuccess() {
    const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    const confettiCount = 50;

    for (let i = 0; i < confettiCount; i++) {
      setTimeout(() => {
        this.createConfetti(colors[Math.floor(Math.random() * colors.length)]);
      }, i * 30);
    }
  }

  static createConfetti(color) {
    const confetti = document.createElement('div');
    confetti.style.position = 'fixed';
    confetti.style.width = '10px';
    confetti.style.height = '10px';
    confetti.style.backgroundColor = color;
    confetti.style.left = Math.random() * 100 + '%';
    confetti.style.top = '-10px';
    confetti.style.opacity = '1';
    confetti.style.transform = 'rotate(0deg)';
    confetti.style.zIndex = '9999';
    confetti.style.pointerEvents = 'none';

    document.body.appendChild(confetti);

    const animation = confetti.animate([
      {
        transform: 'translateY(0) rotate(0deg)',
        opacity: 1
      },
      {
        transform: `translateY(${window.innerHeight}px) rotate(${Math.random() * 720}deg)`,
        opacity: 0
      }
    ], {
      duration: 3000 + Math.random() * 2000,
      easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    });

    animation.onfinish = () => confetti.remove();
  }

  // Smooth number counting animation
  static animateNumber(element, from, to, duration = 1000) {
    const start = performance.now();
    const range = to - from;

    const animate = (currentTime) => {
      const elapsed = currentTime - start;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function
      const eased = progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;

      const currentValue = Math.floor(from + (range * eased));
      element.textContent = currentValue;

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  // Pulse effect for important updates
  static pulseElement(element) {
    element.style.transition = 'transform 0.3s ease-in-out';
    element.style.transform = 'scale(1.1)';

    setTimeout(() => {
      element.style.transform = 'scale(1)';
    }, 300);
  }

  // Shake effect for errors
  static shakeElement(element) {
    element.animate([
      { transform: 'translateX(0)' },
      { transform: 'translateX(-10px)' },
      { transform: 'translateX(10px)' },
      { transform: 'translateX(-10px)' },
      { transform: 'translateX(10px)' },
      { transform: 'translateX(0)' }
    ], {
      duration: 500,
      easing: 'ease-in-out'
    });
  }
}

/* =============================================================================
   Live Demo Presentation Mode
   ============================================================================= */
class PresentationMode {
  static active = false;
  static styleElement = null;

  static enable() {
    this.active = true;

    // Inject presentation mode styles
    this.styleElement = document.createElement('style');
    this.styleElement.textContent = `
      body {
        cursor: none !important;
      }

      * {
        transition: all 0.3s ease !important;
      }

      .card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
      }

      button:hover {
        transform: scale(1.05) !important;
      }

      .metric-value {
        font-size: 3rem !important;
      }
    `;
    document.head.appendChild(this.styleElement);

    // Add spotlight effect
    this.addSpotlight();

    console.log('[Presentation Mode] Enabled');
    NotificationManager.show('Presentation mode activated', 'success');
  }

  static disable() {
    this.active = false;

    if (this.styleElement) {
      this.styleElement.remove();
      this.styleElement = null;
    }

    this.removeSpotlight();

    console.log('[Presentation Mode] Disabled');
  }

  static toggle() {
    if (this.active) {
      this.disable();
    } else {
      this.enable();
    }
  }

  static addSpotlight() {
    const spotlight = document.createElement('div');
    spotlight.id = 'presentation-spotlight';
    spotlight.style.cssText = `
      position: fixed;
      width: 200px;
      height: 200px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(37, 99, 235, 0.3) 0%, transparent 70%);
      pointer-events: none;
      z-index: 9998;
      mix-blend-mode: screen;
    `;
    document.body.appendChild(spotlight);

    document.addEventListener('mousemove', (e) => {
      spotlight.style.left = (e.clientX - 100) + 'px';
      spotlight.style.top = (e.clientY - 100) + 'px';
    });
  }

  static removeSpotlight() {
    const spotlight = document.getElementById('presentation-spotlight');
    if (spotlight) {
      spotlight.remove();
    }
  }
}

/* =============================================================================
   Performance Metrics Display
   ============================================================================= */
class PerformanceMonitor {
  static display = null;

  static show() {
    if (this.display) return;

    this.display = document.createElement('div');
    this.display.id = 'performance-monitor';
    this.display.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      background: rgba(0, 0, 0, 0.8);
      color: #00ff00;
      padding: 12px;
      border-radius: 8px;
      font-family: monospace;
      font-size: 12px;
      z-index: 9999;
      min-width: 200px;
    `;

    document.body.appendChild(this.display);
    this.startMonitoring();
  }

  static hide() {
    if (this.display) {
      this.display.remove();
      this.display = null;
    }
  }

  static startMonitoring() {
    let lastTime = performance.now();
    let frames = 0;

    const update = () => {
      if (!this.display) return;

      frames++;
      const currentTime = performance.now();
      const elapsed = currentTime - lastTime;

      if (elapsed >= 1000) {
        const fps = Math.round((frames * 1000) / elapsed);
        const memory = performance.memory
          ? (performance.memory.usedJSHeapSize / 1048576).toFixed(2)
          : 'N/A';

        this.display.innerHTML = `
          <div>FPS: ${fps}</div>
          <div>Memory: ${memory} MB</div>
          <div>WebSocket: ${AppState.websocket ? '🟢 Connected' : '🔴 Disconnected'}</div>
          <div>Meeting: ${AppState.isRecording ? '🔴 Recording' : '⚪ Idle'}</div>
        `;

        frames = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(update);
    };

    requestAnimationFrame(update);
  }

  static toggle() {
    if (this.display) {
      this.hide();
    } else {
      this.show();
    }
  }
}

/* =============================================================================
   Keyboard Shortcuts for Demo Mode
   ============================================================================= */
class DemoShortcuts {
  static init() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Shift + D: Toggle Demo Mode
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        DemoMode.toggle();
      }

      // Ctrl/Cmd + Shift + P: Toggle Presentation Mode
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        PresentationMode.toggle();
      }

      // Ctrl/Cmd + Shift + M: Toggle Performance Monitor
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'M') {
        e.preventDefault();
        PerformanceMonitor.toggle();
      }

      // Ctrl/Cmd + Shift + S: Start Demo Simulation
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        if (AppState.isRecording) {
          DemoMode.startSimulation();
          NotificationManager.show('Demo simulation started', 'info');
        } else {
          NotificationManager.show('Start a meeting first', 'warning');
        }
      }

      // Ctrl/Cmd + Shift + C: Celebrate with confetti
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        DemoEffects.celebrateSuccess();
      }
    });
  }
}

/* =============================================================================
   Auto-Demo Mode (for unattended demos)
   ============================================================================= */
class AutoDemo {
  static running = false;
  static sequence = null;

  static async start() {
    if (this.running) return;

    this.running = true;
    DemoMode.enable();

    // Sequence of automated actions
    this.sequence = [
      { delay: 1000, action: () => this.typeInField('meeting-title', 'Product Planning Meeting') },
      { delay: 2000, action: () => this.typeInField('participants', 'John, Sarah, Mike, Emily') },
      { delay: 3000, action: () => this.clickButton('meeting-form') },
      { delay: 4000, action: () => DemoMode.startSimulation() },
      { delay: 25000, action: () => this.clickButton('stop-meeting-btn') },
      { delay: 27000, action: () => DemoEffects.celebrateSuccess() }
    ];

    this.executeSequence();
  }

  static stop() {
    this.running = false;
    DemoMode.disable();
  }

  static async executeSequence() {
    for (const step of this.sequence) {
      if (!this.running) break;

      await this.wait(step.delay);
      if (this.running) {
        step.action();
      }
    }
  }

  static typeInField(fieldId, text) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    let i = 0;
    const interval = setInterval(() => {
      if (i < text.length) {
        field.value += text[i];
        i++;
      } else {
        clearInterval(interval);
      }
    }, 100);
  }

  static clickButton(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
      if (button.tagName === 'FORM') {
        button.dispatchEvent(new Event('submit'));
      } else {
        button.click();
      }
    }
  }

  static wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/* =============================================================================
   Demo Control Panel
   ============================================================================= */
class DemoControlPanel {
  static panel = null;

  static show() {
    if (this.panel) return;

    this.panel = document.createElement('div');
    this.panel.id = 'demo-control-panel';
    this.panel.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      background: white;
      border: 2px solid var(--color-gray-300);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
      z-index: 9999;
      min-width: 250px;
      font-size: 14px;
    `;

    this.panel.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <strong>Demo Controls</strong>
        <button onclick="DemoControlPanel.hide()" style="background: none; border: none; cursor: pointer; font-size: 20px;">&times;</button>
      </div>
      <button onclick="DemoMode.toggle()" class="btn btn-primary btn-sm btn-block" style="margin-bottom: 8px;">
        Toggle Demo Mode
      </button>
      <button onclick="PresentationMode.toggle()" class="btn btn-secondary btn-sm btn-block" style="margin-bottom: 8px;">
        Presentation Mode
      </button>
      <button onclick="PerformanceMonitor.toggle()" class="btn btn-outline btn-sm btn-block" style="margin-bottom: 8px;">
        Performance Monitor
      </button>
      <button onclick="AutoDemo.start()" class="btn btn-secondary btn-sm btn-block" style="margin-bottom: 8px;">
        Auto Demo
      </button>
      <button onclick="DemoEffects.celebrateSuccess()" class="btn btn-outline btn-sm btn-block">
        Celebration 🎉
      </button>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--color-gray-200); font-size: 12px; color: var(--color-gray-600);">
        <strong>Shortcuts:</strong><br>
        Ctrl+Shift+D - Demo Mode<br>
        Ctrl+Shift+P - Presentation<br>
        Ctrl+Shift+M - Monitor<br>
        Ctrl+Shift+S - Simulate<br>
        Ctrl+Shift+C - Celebrate
      </div>
    `;

    document.body.appendChild(this.panel);
  }

  static hide() {
    if (this.panel) {
      this.panel.remove();
      this.panel = null;
    }
  }

  static toggle() {
    if (this.panel) {
      this.hide();
    } else {
      this.show();
    }
  }
}

/* =============================================================================
   Initialize Demo Features
   ============================================================================= */
document.addEventListener('DOMContentLoaded', () => {
  DemoShortcuts.init();

  // Add demo control button to navbar
  const navbar = document.querySelector('.navbar-status');
  if (navbar) {
    const demoButton = document.createElement('button');
    demoButton.className = 'btn btn-sm btn-ghost';
    demoButton.style.cssText = 'margin-left: 12px; padding: 4px 8px;';
    demoButton.innerHTML = '🎬';
    demoButton.title = 'Demo Controls';
    demoButton.onclick = () => DemoControlPanel.toggle();
    navbar.parentElement.appendChild(demoButton);
  }

  console.log('[Demo Features] Initialized');
  console.log('[Demo Features] Press Ctrl+Shift+D to enable demo mode');
});

// Export for global access
window.DemoMode = DemoMode;
window.DemoEffects = DemoEffects;
window.PresentationMode = PresentationMode;
window.PerformanceMonitor = PerformanceMonitor;
window.AutoDemo = AutoDemo;
window.DemoControlPanel = DemoControlPanel;
