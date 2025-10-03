/**
 * Meeting Assistant - Enhanced Frontend
 * Modern ES6+ JavaScript with WebSocket, animations, and real-time features
 * @version 2.0.0
 */

/* =============================================================================
   Application State
   ============================================================================= */
const AppState = {
  websocket: null,
  reconnectAttempts: 0,
  maxReconnectAttempts: 10,
  reconnectDelay: 3000,
  reconnectTimer: null,
  isRecording: false,
  meetingStartTime: null,
  durationInterval: null,
  transcriptSegments: [],
  settings: {
    autoScroll: true,
    notifications: true,
    soundEffects: false
  }
};

/* =============================================================================
   WebSocket Management
   ============================================================================= */
class WebSocketManager {
  constructor() {
    this.ws = null;
    this.reconnectTimer = null;
    this.messageQueue = [];
    this.eventHandlers = new Map();
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.scheduleReconnect();
    }
  }

  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('[WebSocket] Connected successfully');
      AppState.reconnectAttempts = 0;
      this.updateConnectionStatus(true);
      this.flushMessageQueue();

      // Notify success
      NotificationManager.show('Connected to server', 'success');
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('[WebSocket] Connection closed', event.code, event.reason);
      this.updateConnectionStatus(false);

      if (!event.wasClean) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
      this.updateConnectionStatus(false);
    };
  }

  handleMessage(message) {
    const { type, data } = message;

    // Emit to registered handlers
    if (this.eventHandlers.has(type)) {
      this.eventHandlers.get(type).forEach(handler => handler(data));
    }

    // Built-in handlers
    switch (type) {
      case 'meeting_started':
        MeetingManager.handleMeetingStarted(data);
        break;
      case 'meeting_stopped':
        MeetingManager.handleMeetingStopped(data);
        break;
      case 'meeting_update':
        MeetingManager.handleMeetingUpdate(data);
        break;
      case 'transcript_update':
        TranscriptManager.addSegment(data);
        break;
      case 'status_update':
        StatusManager.update(data);
        break;
    }
  }

  send(message) {
    if (this.isConnected()) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }

  on(eventType, handler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType).push(handler);
  }

  off(eventType, handler) {
    if (this.eventHandlers.has(eventType)) {
      const handlers = this.eventHandlers.get(eventType);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  scheduleReconnect() {
    if (AppState.reconnectAttempts >= AppState.maxReconnectAttempts) {
      NotificationManager.show('Failed to connect to server', 'danger');
      return;
    }

    AppState.reconnectAttempts++;
    const delay = AppState.reconnectDelay * Math.min(AppState.reconnectAttempts, 5);

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${AppState.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-status');
    const text = document.getElementById('connection-text');

    if (indicator && text) {
      if (connected) {
        indicator.className = 'status-indicator online';
        text.textContent = 'Connected';
      } else {
        indicator.className = 'status-indicator offline';
        text.textContent = 'Disconnected';
      }
    }
  }

  flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (this.ws) {
      this.ws.close();
    }
  }
}

/* =============================================================================
   Meeting Manager
   ============================================================================= */
class MeetingManager {
  static currentMeeting = null;

  static async startMeeting(title, participants) {
    const formData = new FormData();
    // Always append fields, even if empty, to prevent multipart parsing errors
    formData.append('title', title || '');
    formData.append('participants', participants || '');

    try {
      const response = await API.post('/api/meeting/start', formData);

      if (response.success) {
        this.handleMeetingStarted(response);
        NotificationManager.show('Meeting started successfully', 'success');
      } else {
        throw new Error(response.error || 'Failed to start meeting');
      }
    } catch (error) {
      NotificationManager.show(`Failed to start meeting: ${error.message}`, 'danger');
    }
  }

  static async stopMeeting() {
    try {
      const response = await API.post('/api/meeting/stop');

      if (response.success) {
        this.handleMeetingStopped(response);
        NotificationManager.show('Meeting stopped successfully', 'success');
      } else {
        throw new Error(response.error || 'Failed to stop meeting');
      }
    } catch (error) {
      NotificationManager.show(`Failed to stop meeting: ${error.message}`, 'danger');
    }
  }

  static handleMeetingStarted(data) {
    this.currentMeeting = data;
    AppState.isRecording = true;
    AppState.meetingStartTime = new Date();

    // Update UI
    UIManager.showElement('stop-meeting-form');
    UIManager.hideElement('start-meeting-form');
    UIManager.showElement('recording-indicator');

    // Clear transcript
    TranscriptManager.clear();

    // Start duration timer
    this.startDurationTimer();

    // Show waveform animation
    WaveformVisualizer.start();
  }

  static handleMeetingStopped(data) {
    this.currentMeeting = null;
    AppState.isRecording = false;

    // Update UI
    UIManager.hideElement('stop-meeting-form');
    UIManager.showElement('start-meeting-form');
    UIManager.hideElement('recording-indicator');

    // Stop duration timer
    this.stopDurationTimer();

    // Stop waveform animation
    WaveformVisualizer.stop();

    // Show summary if available
    if (data.summary) {
      SummaryManager.display(data.summary);
    }
  }

  static handleMeetingUpdate(data) {
    if (!data.active) return;

    // Update metrics
    MetricsManager.update({
      duration: data.duration,
      wordCount: Math.floor((data.transcript_length || 0) / 5),
      sentiment: data.sentiment || 'neutral'
    });
  }

  static startDurationTimer() {
    this.stopDurationTimer();

    AppState.durationInterval = setInterval(() => {
      if (AppState.meetingStartTime) {
        const duration = Math.floor((new Date() - AppState.meetingStartTime) / 1000);
        MetricsManager.updateDuration(duration);
      }
    }, 1000);
  }

  static stopDurationTimer() {
    if (AppState.durationInterval) {
      clearInterval(AppState.durationInterval);
      AppState.durationInterval = null;
    }
  }
}

/* =============================================================================
   Transcript Manager
   ============================================================================= */
class TranscriptManager {
  static segments = [];

  static addSegment(segment) {
    this.segments.push(segment);
    this.render();

    if (AppState.settings.autoScroll) {
      this.scrollToBottom();
    }
  }

  static clear() {
    this.segments = [];
    this.render();
  }

  static render() {
    const container = document.getElementById('transcript');
    if (!container) return;

    if (this.segments.length === 0) {
      container.innerHTML = `
        <div class="transcript-empty">
          <div class="transcript-empty-icon">🎤</div>
          <div>Start a meeting to see the live transcript here...</div>
        </div>
      `;
      return;
    }

    container.innerHTML = this.segments.map(segment => `
      <div class="transcript-segment">
        <div class="transcript-timestamp">${this.formatTimestamp(segment.timestamp)}</div>
        <div class="transcript-text">${DOMPurify.sanitizeSimple(segment.text)}</div>
      </div>
    `).join('');
  }

  static formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  }

  static scrollToBottom() {
    const container = document.getElementById('transcript');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }

  static getText() {
    return this.segments.map(s => s.text).join('\n');
  }
}

/* =============================================================================
   Metrics Manager
   ============================================================================= */
class MetricsManager {
  static update(metrics) {
    if (metrics.duration !== undefined) {
      this.updateDuration(metrics.duration);
    }
    if (metrics.wordCount !== undefined) {
      this.updateWordCount(metrics.wordCount);
    }
    if (metrics.sentiment !== undefined) {
      this.updateSentiment(metrics.sentiment);
    }
  }

  static updateDuration(seconds) {
    const element = document.getElementById('meeting-duration');
    if (element) {
      element.textContent = this.formatDuration(seconds);
    }
  }

  static updateWordCount(count) {
    const element = document.getElementById('word-count');
    if (element) {
      // Animate count
      this.animateValue(element, parseInt(element.textContent) || 0, count, 500);
    }
  }

  static updateSentiment(sentiment) {
    const element = document.getElementById('sentiment');
    if (element) {
      element.textContent = sentiment;
      element.className = `badge badge-${this.getSentimentColor(sentiment)}`;
    }
  }

  static formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  static animateValue(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const currentValue = Math.floor(start + (range * progress));
      element.textContent = currentValue;

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  static getSentimentColor(sentiment) {
    const colors = {
      positive: 'success',
      neutral: 'secondary',
      negative: 'warning'
    };
    return colors[sentiment] || 'secondary';
  }
}

/* =============================================================================
   Summary Manager
   ============================================================================= */
class SummaryManager {
  static display(summary) {
    const container = document.getElementById('summary-content');
    if (!container) return;

    let html = '';

    if (summary.summary) {
      html += `
        <div class="mb-3">
          <h6>Summary</h6>
          <p>${DOMPurify.sanitizeSimple(summary.summary)}</p>
        </div>
      `;
    }

    if (summary.key_points && summary.key_points.length > 0) {
      html += `
        <div class="mb-3">
          <h6>Key Points</h6>
          <ul>
            ${summary.key_points.map(point => `<li>${DOMPurify.sanitizeSimple(point)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (summary.action_items && summary.action_items.length > 0) {
      html += `
        <div class="mb-3">
          <h6>Action Items</h6>
          <ul class="action-items-list">
            ${summary.action_items.map(item => `
              <li class="action-item">
                <input type="checkbox" class="action-item-checkbox">
                <span class="action-item-text">${DOMPurify.sanitizeSimple(item)}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      `;
    }

    container.innerHTML = html;
    UIManager.showElement('meeting-summary');
  }
}

/* =============================================================================
   Waveform Visualizer
   ============================================================================= */
class WaveformVisualizer {
  static container = null;
  static bars = [];
  static animationId = null;

  static init(containerId = 'waveform-container') {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    // Create waveform bars
    this.bars = [];
    for (let i = 0; i < 5; i++) {
      const bar = document.createElement('div');
      bar.className = 'waveform-bar';
      this.container.appendChild(bar);
      this.bars.push(bar);
    }
  }

  static start() {
    if (!this.container) return;
    this.container.style.display = 'flex';
  }

  static stop() {
    if (!this.container) return;
    this.container.style.display = 'none';
  }
}

/* =============================================================================
   Notification Manager (Toast)
   ============================================================================= */
class NotificationManager {
  static container = null;
  static queue = [];
  static maxNotifications = 3;

  static init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      this.container.id = 'toast-container';
      document.body.appendChild(this.container);
    }
  }

  static show(message, type = 'info', duration = 5000) {
    if (!AppState.settings.notifications) return;

    const toast = this.createToast(message, type);

    // Limit number of visible toasts
    while (this.container.children.length >= this.maxNotifications) {
      this.container.firstChild.remove();
    }

    this.container.appendChild(toast);

    // Auto-dismiss
    setTimeout(() => {
      this.dismiss(toast);
    }, duration);
  }

  static createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
      success: '✓',
      danger: '✕',
      warning: '⚠',
      info: 'ℹ'
    };

    toast.innerHTML = `
      <div class="alert-icon">${icons[type] || icons.info}</div>
      <div class="alert-content">${DOMPurify.sanitizeSimple(message)}</div>
      <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;

    return toast;
  }

  static dismiss(toast) {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }
}

/* =============================================================================
   File Upload Manager
   ============================================================================= */
class FileUploadManager {
  static init(inputId, dropZoneId) {
    const input = document.getElementById(inputId);
    const dropZone = document.getElementById(dropZoneId);

    if (!input || !dropZone) return;

    // File input change
    input.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.handleFile(e.target.files[0]);
      }
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');

      if (e.dataTransfer.files.length > 0) {
        this.handleFile(e.dataTransfer.files[0]);
      }
    });

    // Click to open file dialog
    dropZone.addEventListener('click', () => {
      input.click();
    });
  }

  static handleFile(file) {
    console.log('File selected:', file.name);
    // Override in specific pages
  }

  static showFileInfo(file) {
    const info = {
      name: file.name,
      size: this.formatFileSize(file.size),
      type: file.type || 'Unknown'
    };

    console.log('File info:', info);
    return info;
  }

  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}

/* =============================================================================
   Progress Manager
   ============================================================================= */
class ProgressManager {
  static show(message = 'Processing...', progress = 100) {
    const container = document.getElementById('progress-container');
    const bar = document.getElementById('progress-bar');
    const text = document.getElementById('progress-text');

    if (container) {
      container.style.display = 'block';
    }

    if (bar) {
      bar.style.width = `${progress}%`;
      bar.classList.add('animated');
    }

    if (text) {
      text.innerHTML = `<small class="text-muted">${DOMPurify.sanitizeSimple(message)}</small>`;
    }
  }

  static hide() {
    const container = document.getElementById('progress-container');
    const bar = document.getElementById('progress-bar');

    if (container) {
      container.style.display = 'none';
    }

    if (bar) {
      bar.classList.remove('animated');
    }
  }

  static update(progress, message) {
    const bar = document.getElementById('progress-bar');
    const text = document.getElementById('progress-text');

    if (bar) {
      bar.style.width = `${progress}%`;
    }

    if (message && text) {
      text.innerHTML = `<small class="text-muted">${DOMPurify.sanitizeSimple(message)}</small>`;
    }
  }
}

/* =============================================================================
   API Helper
   ============================================================================= */
class API {
  static async get(url) {
    try {
      const response = await fetch(url);
      return await response.json();
    } catch (error) {
      console.error('API GET error:', error);
      throw error;
    }
  }

  static async post(url, body) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: body instanceof FormData ? body : JSON.stringify(body),
        headers: body instanceof FormData ? {} : { 'Content-Type': 'application/json' }
      });
      return await response.json();
    } catch (error) {
      console.error('API POST error:', error);
      throw error;
    }
  }
}

/* =============================================================================
   UI Manager
   ============================================================================= */
class UIManager {
  static showElement(id) {
    const element = document.getElementById(id);
    if (element) {
      element.style.display = '';
      element.classList.remove('hidden');
    }
  }

  static hideElement(id) {
    const element = document.getElementById(id);
    if (element) {
      element.style.display = 'none';
      element.classList.add('hidden');
    }
  }

  static toggleElement(id) {
    const element = document.getElementById(id);
    if (element) {
      if (element.style.display === 'none') {
        this.showElement(id);
      } else {
        this.hideElement(id);
      }
    }
  }
}

/* =============================================================================
   Status Manager
   ============================================================================= */
class StatusManager {
  static update(status) {
    console.log('Status update:', status);
  }

  static async loadEngineStatus() {
    try {
      const data = await API.get('/api/status');

      if (data.engines) {
        // Update STT engine status
        const sttEngine = data.engines.stt;
        const sttBadge = document.getElementById('stt-engine');
        if (sttBadge) {
          sttBadge.textContent = sttEngine.name || 'Unknown';
          sttBadge.className = `badge ${sttEngine.initialized ? 'badge-success' : 'badge-danger'}`;
        }

        // Update summarization engine status
        const sumEngine = data.engines.summarization;
        const sumBadge = document.getElementById('sum-engine');
        if (sumBadge) {
          sumBadge.textContent = sumEngine.name || 'Unknown';
          sumBadge.className = `badge ${sumEngine.initialized ? 'badge-success' : 'badge-danger'}`;
        }
      }
    } catch (error) {
      console.error('Failed to load engine status:', error);
    }
  }
}

/* =============================================================================
   Keyboard Shortcuts
   ============================================================================= */
class KeyboardShortcuts {
  static init() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K: Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focus search if exists
      }

      // Ctrl/Cmd + S: Start/Stop meeting
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (AppState.isRecording) {
          MeetingManager.stopMeeting();
        } else {
          // Focus on start meeting form
          document.getElementById('meeting-title')?.focus();
        }
      }

      // Escape: Close modals/dialogs
      if (e.key === 'Escape') {
        // Close any open modals
      }
    });
  }
}

/* =============================================================================
   Local Storage Manager
   ============================================================================= */
class StorageManager {
  static save(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }

  static load(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Failed to load from localStorage:', error);
      return defaultValue;
    }
  }

  static remove(key) {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  }
}

/* =============================================================================
   Simple DOM Purify (Sanitization)
   ============================================================================= */
class DOMPurify {
  static sanitizeSimple(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }
}

/* =============================================================================
   Utility Functions
   ============================================================================= */
const Utils = {
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return Promise.resolve();
    }
  },

  downloadText(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  },

  formatDate(date) {
    return new Date(date).toLocaleString();
  }
};

/* =============================================================================
   Application Initialization
   ============================================================================= */
class App {
  static wsManager = null;

  static async init() {
    console.log('[App] Initializing Meeting Assistant...');

    // Load settings from localStorage
    const savedSettings = StorageManager.load('settings');
    if (savedSettings) {
      Object.assign(AppState.settings, savedSettings);
    }

    // Initialize managers
    NotificationManager.init();
    KeyboardShortcuts.init();
    WaveformVisualizer.init();

    // Connect WebSocket
    this.wsManager = new WebSocketManager();
    this.wsManager.connect();

    // Load initial status
    await StatusManager.loadEngineStatus();

    // Mark active nav link
    this.markActiveNavLink();

    console.log('[App] Initialization complete');
  }

  static markActiveNavLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-link').forEach(link => {
      if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
      }
    });
  }

  static cleanup() {
    if (this.wsManager) {
      this.wsManager.disconnect();
    }
    MeetingManager.stopDurationTimer();
    WaveformVisualizer.stop();
  }
}

/* =============================================================================
   Initialize on DOM Ready
   ============================================================================= */
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  App.cleanup();
});

/* =============================================================================
   Export for use in other modules
   ============================================================================= */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    App,
    MeetingManager,
    TranscriptManager,
    NotificationManager,
    API,
    Utils
  };
}
