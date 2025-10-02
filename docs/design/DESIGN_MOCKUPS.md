# Meeting Assistant - Design Mockups & Wireframes

## Table of Contents
1. [Dashboard/Home Screen](#dashboard-home-screen)
2. [Live Meeting View](#live-meeting-view)
3. [Meeting Summary View](#meeting-summary-view)
4. [Settings Screen](#settings-screen)
5. [Transcribe Screen](#transcribe-screen)
6. [Mobile Responsive Views](#mobile-responsive-views)
7. [State Variations](#state-variations)
8. [Component Examples](#component-examples)

---

## Dashboard/Home Screen

### Desktop View (1280px+)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Navigation Bar                                                        🟢 Connected │
│ 🎤 Meeting Assistant   |  Dashboard  Transcribe  Settings           │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌────────────────────────────────────────────────┐
│                      │  │  Live Transcript                            🔴 │
│  📝 Meeting Control  │  │  ┌──────────────────────────────────────────┐ │
│  ┌────────────────┐  │  │  │                                          │ │
│  │ ℹ️ Ready       │  │  │  │  [Waveform visualization]                │ │
│  │ No active      │  │  │  │                                          │ │
│  │ meeting        │  │  │  ├──────────────────────────────────────────┤ │
│  └────────────────┘  │  │  │                                          │ │
│                      │  │  │  🔵 [00:14] John speaking...             │ │
│  Meeting Title *     │  │  │  The new feature looks great.            │ │
│  [Team Standup    ]  │  │  │                                          │ │
│                      │  │  │  🟣 [00:42] Sarah speaking...            │ │
│  Participants        │  │  │  I agree, we should deploy next week.    │ │
│  [John, Sarah     ]  │  │  │                                          │ │
│                      │  │  │  🔵 [01:15] John speaking...             │ │
│  ┌────────────────┐  │  │  │  Perfect, I'll prepare the docs.         │ │
│  │ ▶ Start Meeting│  │  │  │                                          │ │
│  └────────────────┘  │  │  │  ⬇️ Auto-scrolling enabled              │ │
│                      │  │  └──────────────────────────────────────────┘ │
│  ─────────────────   │  │                                               │
│                      │  │  📋 [Copy]  💾 [Download]                    │
│  ⚙️ Engine Status    │  └────────────────────────────────────────────────┘
│  ┌────────────────┐  │
│  │ Speech-to-Text │  │  ┌────────────────────────────────────────────────┐
│  │ ✅ whisper     │  │  │  ✨ Meeting Summary                            │
│  │ ▓▓▓▓░░░░ 60%   │  │  │  ┌──────────────────────────────────────────┐ │
│  │                │  │  │  │  Summary                                 │ │
│  │ Summarization  │  │  │  │  The team discussed the new feature and  │ │
│  │ ✅ groq        │  │  │  │  agreed to deploy next week. John will   │ │
│  │ ▓▓▓▓▓░░░ 80%   │  │  │  │  prepare the documentation.              │ │
│  │                │  │  │  ├──────────────────────────────────────────┤ │
│  │ [🔄 Refresh]   │  │  │  │  Key Points                              │ │
│  └────────────────┘  │  │  │  • New feature ready for deployment      │ │
│                      │  │  │  • Target: Next week                     │ │
│  ─────────────────   │  │  │  • Documentation needed                  │ │
│                      │  │  │                                          │ │
│  📊 Live Metrics     │  │  │  Action Items                            │ │
│  (Hidden when idle)  │  │  │  ☐ Prepare deployment documentation      │ │
│  ┌────────────────┐  │  │  │  ☐ Schedule deployment meeting           │ │
│  │ DURATION       │  │  │  └──────────────────────────────────────────┘ │
│  │ 05:42          │  │  │                                               │
│  │                │  │  │  [Copy] [Download] [Share]                    │
│  │ WORD COUNT     │  │  └────────────────────────────────────────────────┘
│  │ 127            │  │
│  └────────────────┘  │
└──────────────────────┘

Footer: Meeting Assistant v2.0.0 - AI-powered meeting transcription
```

### Key Features
1. **Left sidebar (380px)**: Sticky, contains all controls
2. **Main area (flex)**: Transcript and summary
3. **Visual hierarchy**: Clear separation of sections
4. **Status indicators**: Color-coded badges
5. **Progress bars**: Visual engine status
6. **Waveform animation**: Active during recording

---

## Live Meeting View (Recording State)

### Active Recording

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🎤 Meeting Assistant - Team Standup Meeting                    🔴 REC 05:42  │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌─────────────────────────────────────────────────┐
│                      │  │  Live Transcript                         🔴 REC  │
│  🔴 Meeting Control  │  │  ┌───────────────────────────────────────────┐  │
│  ┌────────────────┐  │  │  │                                           │  │
│  │ 🟢 Recording   │  │  │  │  ┌─┐ ┌──┐ ┌───┐ ┌──┐ ┌─┐                │  │
│  │ Team Standup   │  │  │  │  │ │ │  │ │   │ │  │ │ │ Waveform      │  │
│  └────────────────┘  │  │  │  └─┘ └──┘ └───┘ └──┘ └─┘                │  │
│                      │  │  │                                           │  │
│  [Waveform viz]      │  │  ├───────────────────────────────────────────┤  │
│  ┌─┐ ┌──┐ ┌───┐     │  │  │                                           │  │
│  │ │ │  │ │   │     │  │  │  [00:14] 👤 John                         │  │
│  └─┘ └──┘ └───┘     │  │  │  The new feature looks great and I think │  │
│                      │  │  │  we should move forward with deployment.  │  │
│  ┌────────────────┐  │  │  │                                           │  │
│  │ ⏹ Stop Meeting │  │  │  │  [00:42] 👤 Sarah                        │  │
│  └────────────────┘  │  │  │  I completely agree. The testing phase   │  │
│                      │  │  │  went smoothly and we're ready.           │  │
│  ─────────────────   │  │  │                                           │  │
│                      │  │  │  [01:15] 👤 John                         │  │
│  📊 Live Metrics     │  │  │  Perfect! I'll start preparing the       │  │
│  ┌────────────────┐  │  │  │  documentation this afternoon...         │  │
│  │ DURATION       │  │  │  │                                           │  │
│  │ 05:42          │  │  │  │  [01:48] 👤 Mike                         │  │
│  │ ⏱️ counting up  │  │  │  │  Sounds good. I can help with the       │  │
│  │                │  │  │  │  deployment checklist.                    │  │
│  │ WORDS          │  │  │  │                                           │  │
│  │ 267            │  │  │  │  [02:03] 👤 Sarah                        │  │
│  │ 📈 updating     │  │  │  │  Thanks Mike! Let's sync on...          │  │
│  │                │  │  │  │                                           │  │
│  │ SPEAKERS       │  │  │  │  ⬇️ Auto-scrolling to latest message    │  │
│  │ 3 active       │  │  │  └───────────────────────────────────────────┘  │
│  └────────────────┘  │  │                                                  │
│                      │  │  Duration: 05:42 | Words: 267 | 🔴 Recording    │
│  ⚙️ Engine Status    │  └─────────────────────────────────────────────────┘
│  ┌────────────────┐  │
│  │ STT: ✅ 100%   │  │
│  │ Sum: ⚡ Ready  │  │
│  └────────────────┘  │
└──────────────────────┘
```

### Recording Indicator Details
- **Pulsing red dot**: Animated, 1.5s cycle
- **REC badge**: Always visible in header
- **Waveform**: Real-time audio amplitude visualization
- **Live metrics**: Update every second
- **Speaker labels**: Color-coded per speaker
- **Auto-scroll**: Smooth scroll to newest message

---

## Meeting Summary View

### Post-Meeting Summary Display

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ✨ Meeting Summary                                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  📋 Executive Summary                                                  │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │  The team discussed deployment of the new feature. All testing   │  │  │
│  │  │  completed successfully. John will prepare documentation and     │  │  │
│  │  │  Mike will assist with deployment checklist. Target: Next week.  │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  🔑 Key Points                                                         │  │
│  │  ┌─────────────────────────┐  ┌──────────────────────────┐            │  │
│  │  │ ✓ New feature complete  │  │ ✓ Testing successful     │            │  │
│  │  │ 👥 Team: John, Sarah,   │  │ 📅 Deploy: Next week     │            │  │
│  │  │    Mike                 │  │ 📝 Docs needed           │            │  │
│  │  └─────────────────────────┘  └──────────────────────────┘            │  │
│  │                                                                        │  │
│  │  ✅ Action Items                                                       │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │  ☐ Prepare deployment documentation (John)                       │  │  │
│  │  │  ☐ Create deployment checklist (Mike)                            │  │  │
│  │  │  ☐ Schedule deployment meeting (Sarah)                           │  │  │
│  │  │  ☐ Review final test results (All)                               │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  📊 Meeting Analytics                                                  │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │  │
│  │  │  Duration       │  │  Participants   │  │  Word Count     │        │  │
│  │  │  ⏱️ 05:42       │  │  👥 3 people    │  │  💬 267 words   │        │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │  │
│  │                                                                        │  │
│  │  🎤 Speaking Time                                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │  John   ▓▓▓▓▓▓▓▓▓░░░░░░░░ 45%   2:34                             │  │  │
│  │  │  Sarah  ▓▓▓▓▓▓░░░░░░░░░░░ 35%   2:00                             │  │  │
│  │  │  Mike   ▓▓▓░░░░░░░░░░░░░░ 20%   1:08                             │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  💭 Sentiment Analysis                                                 │  │
│  │  Overall: 😊 Positive   Confidence: 92%                               │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │  Positive ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░ 85%                                    │  │  │
│  │  │  Neutral  ▓▓░░░░░░░░░░░░░ 12%                                    │  │  │
│  │  │  Negative ░░░░░░░░░░░░░░░  3%                                    │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  [📋 Copy]  [💾 Download PDF]  [📧 Email]  [🔗 Share Link]                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Summary Features
1. **Visual cards**: Gradient backgrounds for importance
2. **Interactive checkboxes**: Action items can be checked off
3. **Analytics charts**: Visual representation of data
4. **Speaking time breakdown**: Horizontal bar chart
5. **Sentiment analysis**: Color-coded sentiment distribution
6. **Export options**: Multiple formats available

---

## Settings Screen

### Engine Configuration

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                                                 │
└──────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│  🎛️ Engine Configuration                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  Speech-to-Text Engine                                              │  │
│  │  ┌────────────────────────────────────────────────────────────────┐  │  │
│  │  │  ⚡ Whisper (OpenAI)                                        ▼  │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │  Current: whisper-large-v3  |  Status: ✅ Ready                     │  │
│  │                                                                      │  │
│  │  Model Size:                                                         │  │
│  │  ( ) tiny   (•) base   ( ) small   ( ) medium   ( ) large           │  │
│  │                                                                      │  │
│  │  Language:                                                           │  │
│  │  [English (US)                                              ▼]       │  │
│  │                                                                      │  │
│  │  ────────────────────────────────────────────────────────────────   │  │
│  │                                                                      │  │
│  │  Summarization Engine                                               │  │
│  │  ┌────────────────────────────────────────────────────────────────┐  │  │
│  │  │  🚀 Groq (Fast LLM)                                        ▼  │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │  Current: mixtral-8x7b  |  Status: ✅ Ready                         │  │
│  │                                                                      │  │
│  │  Summary Length:                                                     │  │
│  │  ( ) Brief   (•) Standard   ( ) Detailed                            │  │
│  │                                                                      │  │
│  │  [✓] Include key points                                             │  │
│  │  [✓] Extract action items                                           │  │
│  │  [✓] Identify speakers                                              │  │
│  │  [ ] Sentiment analysis                                             │  │
│  │                                                                      │  │
│  │                                  [Apply Changes]                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  🎤 Audio Configuration                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Input Device                                                        │  │
│  │  [🎙️ Built-in Microphone                                        ▼]  │  │
│  │                                                                      │  │
│  │  Sample Rate:  [16 kHz ▼]   |   Channels:  [Mono ▼]                │  │
│  │                                                                      │  │
│  │  Input Level: ▓▓▓▓▓▓▓▓░░░░░░░░░░ 52%                                │  │
│  │                                                                      │  │
│  │  [🎤 Test Microphone]      [🔇 Mute Test]                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  🔧 Processing Settings                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Real-time Transcription    [●────────] ON                          │  │
│  │  Auto-generate Summary      [●────────] ON                          │  │
│  │  Speaker Detection          [──────────●] OFF                       │  │
│  │  Save Recordings            [──────────●] OFF                       │  │
│  │                                                                      │  │
│  │  Chunk Duration (seconds):  [30                    ]                 │  │
│  │  Max Meeting Duration:      [4 hours               ]                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  [Save All Settings]                                     [Reset Defaults]   │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐
│  ℹ️ System Information      │
│  ┌───────────────────────┐  │
│  │ Version: 2.0.0        │  │
│  │ Audio Devices: 3      │  │
│  │ STT Engines: 2        │  │
│  │ Sum Engines: 3        │  │
│  │                       │  │
│  │ Data Dir:             │  │
│  │ /data/meetings/       │  │
│  │                       │  │
│  │ Models Dir:           │  │
│  │ /models/              │  │
│  └───────────────────────┘  │
│                             │
│  Quick Actions              │
│  [📥 Download Models]       │
│  [📂 Open Data Folder]      │
│  [📊 Performance]           │
│  [🔄 Restart Services]      │
└─────────────────────────────┘
```

### Settings Features
1. **Dropdown selectors**: Engine selection
2. **Radio buttons**: Model size options
3. **Toggle switches**: iOS-style animated
4. **Progress sliders**: Input level visualization
5. **Info sidebar**: System information
6. **Quick actions**: One-click utilities

---

## Transcribe Screen

### File Upload Interface

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  📝 Transcribe Audio File                                                    │
└──────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  📤 Upload Audio File                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐│
│  │                                                                        ││
│  │                            ┌─────────┐                                 ││
│  │                            │   📁   │                                 ││
│  │                            │  64px  │                                 ││
│  │                            └─────────┘                                 ││
│  │                                                                        ││
│  │                   Click to upload or drag & drop                       ││
│  │                                                                        ││
│  │             WAV, MP3, M4A, FLAC, OGG (Max 500MB)                       ││
│  │                                                                        ││
│  └────────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  📊 Processing Status                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐│
│  │  ℹ️ Ready to process files                                             ││
│  │                                                                        ││
│  │  [When processing:]                                                    ││
│  │  ⚡ Processing "team-meeting.wav"...                                   ││
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ 68% Complete                                    ││
│  │                                                                        ││
│  │  Estimated time remaining: 1m 23s                                      ││
│  └────────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  📄 Transcription Results                                                   │
│  ┌────────────────────────────────────────────────────────────────────────┐│
│  │                                                                        ││
│  │  The team discussed the upcoming product launch. Sarah mentioned      ││
│  │  that the marketing materials are ready and will be distributed       ││
│  │  next week. John confirmed that the development is complete and       ││
│  │  all tests are passing. Mike raised concerns about the deployment     ││
│  │  timeline and suggested adding a buffer day for unexpected issues.    ││
│  │  The team agreed to push the launch date by one day to accommodate    ││
│  │  this suggestion. Action items were assigned to each team member.     ││
│  │                                                                        ││
│  └────────────────────────────────────────────────────────────────────────┘│
│                                                                            │
│  Engine: whisper-base  |  Language: en-US  |  Confidence: 94%             │
│                                                                            │
│  [Copy] [Download] [Summarize]                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  ✨ Text Summarization                                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐│
│  │  Paste your meeting transcript or any text here...                    ││
│  │                                                                        ││
│  │  [Large text area - 6 rows minimum]                                   ││
│  │                                                                        ││
│  │                                                                        ││
│  └────────────────────────────────────────────────────────────────────────┘│
│                                                                            │
│  [Generate Summary]                                                        │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│  💡 Tips                │
│  ┌───────────────────┐  │
│  │ ✓ Use high-quality│  │
│  │   audio files     │  │
│  │                   │  │
│  │ ✓ WAV format for  │  │
│  │   best accuracy   │  │
│  │                   │  │
│  │ ✓ Reduce noise    │  │
│  │   when possible   │  │
│  │                   │  │
│  │ ✓ Clear speech    │  │
│  │   improves quality│  │
│  └───────────────────┘  │
│                         │
│  📁 Recent Files        │
│  • team-meeting.wav     │
│  • client-call.mp3      │
│  • standup-mon.m4a      │
└─────────────────────────┘
```

### File Upload Features
1. **Drag-and-drop zone**: Large, obvious target
2. **Dashed border**: Indicates drop zone
3. **Progress bar**: Animated during upload
4. **File validation**: Shows accepted formats
5. **Recent files**: Quick re-processing
6. **Tips sidebar**: Helpful best practices

---

## Mobile Responsive Views

### Mobile Dashboard (< 640px)

```
┌──────────────────┐
│ 🎤 Meeting Asst  │
│            ☰     │
└──────────────────┘

┌──────────────────┐
│                  │
│ 📝 Quick Start   │
│ ┌──────────────┐ │
│ │ ℹ️ Ready     │ │
│ └──────────────┘ │
│                  │
│ Meeting Title *  │
│ [Team Standup ]  │
│                  │
│ Participants     │
│ [John, Sarah  ]  │
│                  │
│ ┌──────────────┐ │
│ │ ▶ Start      │ │
│ └──────────────┘ │
└──────────────────┘

┌──────────────────┐
│ ⚙️ Engine Status  │
│ ┌──────────────┐ │
│ │ STT: ✅ Ready│ │
│ │ Sum: ✅ Ready│ │
│ └──────────────┘ │
└──────────────────┘

┌──────────────────┐
│ 📄 Transcript    │
│ ┌──────────────┐ │
│ │              │ │
│ │ 🎤 Start a   │ │
│ │ meeting to   │ │
│ │ see live     │ │
│ │ transcript   │ │
│ │              │ │
│ └──────────────┘ │
│ [Copy] [Save]    │
└──────────────────┘

┌──────────────────┐
│ ⬡ ⬡ ⬡ ⬡ ⬡       │
│ Nav Tabs         │
└──────────────────┘
```

### Mobile Features
1. **Hamburger menu**: Collapsible navigation
2. **Stack layout**: Single column
3. **Bottom tabs**: Primary navigation
4. **Larger touch targets**: 44px minimum
5. **Condensed metrics**: Single column
6. **Sticky header**: Always visible
7. **Floating action button**: Quick start

### Tablet View (640px - 1024px)

```
┌───────────────────────────────────────────┐
│ 🎤 Meeting Assistant        🟢 Connected  │
└───────────────────────────────────────────┘

┌─────────────────┐ ┌───────────────────────┐
│                 │ │                       │
│ 📝 Control      │ │ 📄 Transcript         │
│                 │ │                       │
│ [Start Form]    │ │ [Transcript Area]     │
│                 │ │                       │
│ ⚙️ Status       │ │                       │
│                 │ │                       │
│ [Engines]       │ │ [Copy] [Download]     │
│                 │ │                       │
└─────────────────┘ └───────────────────────┘

┌───────────────────────────────────────────┐
│ ✨ Summary (Full Width When Shown)        │
│                                           │
│ [Summary Content]                         │
└───────────────────────────────────────────┘
```

---

## State Variations

### Loading State

```
┌────────────────────────────────────────┐
│  Processing...                         │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │    ⏳ Loading (Spinner)          │  │
│  │                                  │  │
│  │    Processing your request...    │  │
│  │                                  │  │
│  │    ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ 52%     │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

### Empty State

```
┌────────────────────────────────────────┐
│  No Meetings Yet                       │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │         🎤 (Large Icon)          │  │
│  │                                  │  │
│  │     Start your first meeting     │  │
│  │                                  │  │
│  │  Click "Start Meeting" to begin  │  │
│  │  recording and transcribing      │  │
│  │                                  │  │
│  │     ┌──────────────────┐         │  │
│  │     │  Get Started  →  │         │  │
│  │     └──────────────────┘         │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

### Error State

```
┌────────────────────────────────────────┐
│  ⚠️ Error                              │
│  ┌──────────────────────────────────┐  │
│  │  ❌                              │  │
│  │                                  │  │
│  │  Failed to start meeting         │  │
│  │                                  │  │
│  │  Could not connect to            │  │
│  │  microphone. Please check        │  │
│  │  permissions.                    │  │
│  │                                  │  │
│  │  [Try Again]  [View Help]        │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

### Success State

```
┌────────────────────────────────────────┐
│  ✅ Success                            │
│  ┌──────────────────────────────────┐  │
│  │  ✓ (Checkmark with pulse)        │  │
│  │                                  │  │
│  │  Meeting saved successfully!     │  │
│  │                                  │  │
│  │  Summary has been generated      │  │
│  │  and saved to your library.      │  │
│  │                                  │  │
│  │  [View Summary]  [Start New]     │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

---

## Component Examples

### Button Variations

```
Primary Button:
┌────────────────┐
│ ▶ Start Meeting│  (Indigo, white text, shadow)
└────────────────┘

Secondary Button:
┌────────────────┐
│ 🔄 Refresh     │  (Green, white text)
└────────────────┘

Danger Button:
┌────────────────┐
│ ⏹ Stop Meeting │  (Red, white text)
└────────────────┘

Ghost Button:
┌────────────────┐
│ 📋 Copy        │  (Transparent, border, gray text)
└────────────────┘

Icon Button:
┌───┐
│ ⚙️ │  (Small, circular)
└───┘
```

### Form Inputs

```
Text Input (Default):
┌────────────────────────────────┐
│ Team Standup                   │
└────────────────────────────────┘

Text Input (Focused):
┌────────────────────────────────┐
│ Team Standup|                  │  (Blue border, ring)
└────────────────────────────────┘

Text Input (Error):
┌────────────────────────────────┐
│                                │  (Red border)
└────────────────────────────────┘
⚠️ Title is required

Select Dropdown:
┌────────────────────────────────┐
│ Whisper (OpenAI)            ▼ │
└────────────────────────────────┘

Toggle Switch (OFF):
──────────○

Toggle Switch (ON):
○──────────  (Blue background)
```

### Cards

```
Standard Card:
┌──────────────────────────┐
│ Header                   │
├──────────────────────────┤
│                          │
│ Content area             │
│                          │
├──────────────────────────┤
│ Footer                   │
└──────────────────────────┘

Elevated Card:
  ┌────────────────────────┐
  │ Elevated               │  (Higher shadow, no border)
  │                        │
  │ Content                │
  └────────────────────────┘

Gradient Card:
┌──────────────────────────┐
│ ┌────────────────────┐   │
│ │ Gradient Header    │   │  (Purple to blue gradient)
│ └────────────────────┘   │
│                          │
│ Content                  │
└──────────────────────────┘
```

### Badges

```
Success Badge:   ✅ Ready
Error Badge:     ❌ Failed
Warning Badge:   ⚠️ Warning
Info Badge:      ℹ️ Info
Secondary Badge: ⚪ Default
```

### Progress Indicators

```
Linear Progress:
▓▓▓▓▓▓▓▓░░░░░░░░░░ 45%

Linear Progress (Animated):
▓▓▓▓▓▓▓▓░░░░░░░░░░  (Shimmer effect)

Circular Spinner:
    ⏳   (Rotating)

Progress with Steps:
① ─●─ ② ─○─ ③ ─○─ ④
```

### Alert/Toast Notifications

```
Success Toast:
┌────────────────────────────┐
│ ✓ Meeting started!    [×] │  (Green border, light green bg)
└────────────────────────────┘

Error Toast:
┌────────────────────────────┐
│ ✕ Connection failed!  [×] │  (Red border, light red bg)
└────────────────────────────┘

Info Toast:
┌────────────────────────────┐
│ ℹ Processing...       [×] │  (Blue border, light blue bg)
└────────────────────────────┘
```

---

## Animation Examples

### Micro-interactions (Text Descriptions)

**Button Hover:**
- Transform: scale(1.02)
- Shadow: Increases from sm to md
- Duration: 150ms
- Easing: ease-out

**Card Hover:**
- Transform: translateY(-2px)
- Shadow: Increases from sm to md
- Duration: 250ms
- Easing: ease-out

**Input Focus:**
- Border color: gray → primary
- Box-shadow: Ring appears (3px spread, 10% opacity)
- Duration: 150ms
- Easing: ease-out

**Waveform Animation:**
- Bars scale vertically from 8px to 32px
- Staggered delays (0s, 0.1s, 0.2s, 0.3s, 0.4s)
- Duration: 1.2s
- Loop: Infinite
- Easing: ease-in-out

**Recording Indicator Pulse:**
- Opacity: 1 → 0.6 → 1
- Box-shadow: 0px spread → 8px spread → 0px
- Duration: 1.5s
- Loop: Infinite
- Easing: ease-in-out

**Toast Slide In:**
- Transform: translateX(100%) → translateX(0)
- Opacity: 0 → 1
- Duration: 250ms
- Easing: ease-out

**Loading Shimmer:**
- Background position: -100% → 100%
- Duration: 1.5s
- Loop: Infinite
- Easing: linear

---

## Accessibility Annotations

### Screen Reader Experience

```
[Dashboard]
Landmark: Main Navigation
  - Link: "Dashboard" (current page)
  - Link: "Transcribe"
  - Link: "Settings"
  - Status: "Connected" (live region, polite)

Landmark: Main Content (Skip link target)
  Region: "Meeting Control"
    - Heading Level 2: "Meeting Control"
    - Status: "Ready, No active meeting" (live region, polite)
    - Form: "Start new meeting"
      - Label: "Meeting Title" (required)
      - Input: text field
      - Label: "Participants" (optional)
      - Input: text field
      - Button: "Start Meeting"

  Region: "Live Transcript"
    - Heading Level 2: "Live Transcript"
    - Status: "Recording" (live region, assertive) [when active]
    - Log region: Transcript messages (live region, polite)
    - Button: "Copy transcript"
    - Button: "Download transcript"
```

### Keyboard Navigation

```
Tab Order:
1. Skip to main content link
2. Navigation: Dashboard link
3. Navigation: Transcribe link
4. Navigation: Settings link
5. Meeting Title input
6. Participants input
7. Start Meeting button
8. Refresh Status button
9. Copy transcript button
10. Download transcript button
[Continue through all interactive elements...]

Keyboard Shortcuts:
- Ctrl/Cmd + K: Focus search
- Ctrl/Cmd + S: Start/Stop meeting
- Ctrl/Cmd + C: Copy transcript (when focused)
- Escape: Close modals
- Arrow keys: Navigate lists
- Space: Toggle checkboxes
- Enter: Activate buttons
```

### Focus Indicators

```
Default Focus (visible):
┌────────────────┐
│ Button         │  ← 2px blue outline, 2px offset
└────────────────┘

Link Focus:
[Dashboard]  ← 2px blue outline with border-radius
```

---

## Color Palette Reference

### Brand Colors (Visual)
```
Primary:    ███ #6366F1 (Indigo)
Secondary:  ███ #8B5CF6 (Purple)
Success:    ███ #10B981 (Emerald)
Warning:    ███ #F59E0B (Amber)
Error:      ███ #EF4444 (Red)
Info:       ███ #3B82F6 (Blue)
```

### Neutral Grays
```
Gray 50:    ███ #F9FAFB (Lightest)
Gray 100:   ███ #F3F4F6
Gray 200:   ███ #E5E7EB
Gray 300:   ███ #D1D5DB
Gray 400:   ███ #9CA3AF
Gray 500:   ███ #6B7280
Gray 600:   ███ #4B5563
Gray 700:   ███ #374151
Gray 800:   ███ #1F2937
Gray 900:   ███ #111827 (Darkest)
```

---

## Typography Scale

```
Hero (3rem):      Meeting Assistant
Page Title (2.25rem):  Dashboard
Section (1.875rem):     Live Transcript
Heading (1.5rem):       Engine Status
Subheading (1.25rem):   Meeting Control
Body (1rem):            Regular text content
Small (0.875rem):       Helper text
Tiny (0.75rem):         Captions, timestamps
```

---

## Conclusion

These mockups represent a modern, accessible, and visually impressive design system for the Meeting Assistant application. The design prioritizes:

1. **Clarity**: Clear visual hierarchy and intuitive layouts
2. **Efficiency**: Quick access to primary actions
3. **Feedback**: Real-time visual feedback for all interactions
4. **Accessibility**: WCAG 2.1 AA compliant design
5. **Responsiveness**: Optimized for all screen sizes
6. **Delight**: Thoughtful animations and micro-interactions

The design system is comprehensive, scalable, and ready for implementation.
