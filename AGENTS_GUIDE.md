# Claude Code Subagents Guide

## 📦 Installed Agents

Your Meeting Assistant project now has **12 specialized AI agents** ready to use:

### 🐍 Python Pro
**Location:** `.claude/agents/python-pro.md`
- **Expertise:** Python 3.10+, AsyncIO, FastAPI, Type Hints
- **Use for:** Code optimization, async improvements, Python best practices

### 🤖 AI Engineer
**Location:** `.claude/agents/ai-engineer.md`
- **Expertise:** LLM applications, RAG systems, prompt engineering
- **Use for:** Improving summarization, model integration, AI pipelines

### 🔬 ML Engineer
**Location:** `.claude/agents/ml-engineer.md`
- **Expertise:** ML pipelines, model serving, feature engineering
- **Use for:** Model optimization, NPU acceleration, inference tuning

### 🔍 Code Reviewer
**Location:** `.claude/agents/code-reviewer.md`
- **Expertise:** Code quality, security, performance review
- **Use for:** Code reviews, security audits, best practices

### 🐛 Debugger
**Location:** `.claude/agents/debugger.md`
- **Expertise:** Bug fixing, root cause analysis
- **Use for:** Troubleshooting errors, debugging issues

### ⚡ Performance Engineer
**Location:** `.claude/agents/performance-engineer.md`
- **Expertise:** Profiling, optimization, benchmarking
- **Use for:** Performance tuning, memory optimization, speed improvements

### 🧪 Test Automator
**Location:** `.claude/agents/test-automator.md`
- **Expertise:** Unit testing, integration tests, pytest
- **Use for:** Writing tests, improving coverage, test automation

### 🏗️ API Designer
**Location:** `.claude/agents/api-designer.md`
- **Expertise:** REST APIs, FastAPI, OpenAPI documentation
- **Use for:** API design, documentation, endpoint optimization

### 💻 Frontend Developer
**Location:** `.claude/agents/frontend-developer.md`
- **Expertise:** React 18+, Vue 3+, Angular 15+, TypeScript, Web Performance
- **Use for:** Building UI components, state management, accessibility, responsive design

### 🎨 UI Designer
**Location:** `.claude/agents/ui-designer.md`
- **Expertise:** Visual design, design systems, Figma, interaction patterns
- **Use for:** Creating beautiful interfaces, design systems, color/typography, prototyping

### 🧩 UI/UX Designer
**Location:** `.claude/agents/ui-ux-designer.md`
- **Expertise:** User research, accessibility-first design, design tokens, UX strategy
- **Use for:** User research, journey mapping, accessibility compliance, cross-platform design

### ✅ UI Visual Validator
**Location:** `.claude/agents/ui-visual-validator.md`
- **Expertise:** Visual testing, design system compliance, accessibility verification
- **Use for:** Validating UI changes, visual regression testing, WCAG compliance checking

## 🚀 How to Use Agents

### Method 1: Direct Agent Call (Explicit)
```bash
# In Claude Code CLI or chat
@agent-python-pro Review my async audio streaming code in src/audio/

@agent-code-reviewer Check src/meeting.py for code quality issues

@agent-performance-engineer Optimize the Whisper integration
```

### Method 2: Auto-Selection (Recommended)
Let Claude automatically choose the right agent based on your request:

```bash
# Claude will use python-pro agent
"Improve the type hints in my codebase"

# Claude will use ai-engineer agent
"Help me optimize the meeting summarization prompts"

# Claude will use performance-engineer agent
"My transcription is slow, can you optimize it?"
```

### Method 3: Contextual Usage
```bash
# Start conversation, Claude picks agent
"I need to add RAG capabilities to my summarization"
# → Uses ai-engineer

"Write comprehensive tests for the STT engines"
# → Uses test-automator

"Debug why audio recording fails on RK3588"
# → Uses debugger
```

## 🎯 Common Use Cases

### Optimize Performance
```
Ask performance-engineer to:
- Profile STT engine bottlenecks
- Reduce memory usage for SBC deployment
- Optimize real-time transcription speed
```

### Improve Code Quality
```
Ask code-reviewer to:
- Review meeting.py for best practices
- Check for security vulnerabilities
- Validate error handling patterns
```

### Add AI Features
```
Ask ai-engineer to:
- Implement RAG for context-aware summaries
- Improve prompt engineering for Qwen
- Build custom AI pipeline for meetings
```

### Debug Issues
```
Ask debugger to:
- Fix model loading errors
- Troubleshoot NPU acceleration
- Resolve memory leaks in long meetings
```

### Write Tests
```
Ask test-automator to:
- Create unit tests for STT engines
- Add integration tests for web app
- Improve test coverage to 80%+
```

## 🖥️ Testing UI

Open the agent tester UI to explore agents interactively:

```bash
# Open in browser
firefox agent_tester.html
# or
google-chrome agent_tester.html
# or
xdg-open agent_tester.html
```

The UI provides:
- Visual agent selection
- Task input interface
- Example use cases for each agent
- Quick reference for commands

## 📚 Additional Agents Available

You have **400+ more agents** in `~/claude-subagents-library/`:

### Install More Agents
```bash
# Example: Add frontend developer for web UI
cp ~/claude-subagents-library/awesome-claude-code-subagents/categories/01-core-development/frontend-developer.md .claude/agents/

# Add Docker specialist
cp ~/claude-subagents-library/awesome-claude-code-subagents/categories/03-infrastructure/docker-specialist.md .claude/agents/

# Add security auditor
cp ~/claude-subagents-library/awesome-claude-code-subagents/categories/04-quality-security/security-auditor.md .claude/agents/
```

### Browse Available Agents
```bash
# List all VoltAgent categories
ls ~/claude-subagents-library/awesome-claude-code-subagents/categories/

# List all wshobson agents
ls ~/claude-subagents-library/wshobson-agents/

# List all 0xfurai agents
ls ~/claude-subagents-library/claude-code-subagents/agents/
```

## 🛠️ Agent Management

### List Active Agents
```bash
ls -la .claude/agents/
```

### Remove Agent
```bash
rm .claude/agents/debugger.md
```

### Install from Library
```bash
cp ~/claude-subagents-library/[repo]/[path]/[agent].md .claude/agents/
```

### Install Globally (All Projects)
```bash
cp [agent].md ~/.claude/agents/
```

## 💡 Pro Tips

1. **Let Claude Choose**: Don't always specify the agent - Claude is smart about auto-selection
2. **Combine Agents**: Use multiple agents in sequence (e.g., python-pro → code-reviewer → test-automator)
3. **Project-Specific**: Keep agents in `.claude/agents/` to version control with your project
4. **User-Level**: Put commonly used agents in `~/.claude/agents/` for all projects
5. **Test UI**: Use `agent_tester.html` to preview agents before committing to your workflow

## 🔗 Resources

- **Agent Library:** `~/claude-subagents-library/`
- **VoltAgent (100+ agents):** `awesome-claude-code-subagents/`
- **wshobson (84 agents):** `wshobson-agents/`
- **0xfurai (137 agents):** `claude-code-subagents/`
- **davepoon (117 + CLI):** `claude-code-subagents-collection/`

## 📖 Examples for Your Project

### Scenario 1: Optimize Whisper Performance
```
"@agent-performance-engineer I need to optimize Whisper model loading and inference
for the RK3588 SBC. Current speed is 0.5x realtime, target is 2x."
```

### Scenario 2: Add Comprehensive Tests
```
"@agent-test-automator Create a complete test suite for src/stt/ including:
- Unit tests for each engine
- Mock audio fixtures
- Integration tests
- Aim for 85% coverage"
```

### Scenario 3: Improve Summarization
```
"@agent-ai-engineer Help me improve the meeting summarization quality.
Current model is Qwen 2.5-3B. Consider:
- Better prompts
- RAG for past meetings
- Custom fine-tuning"
```

### Scenario 4: Code Review
```
"@agent-code-reviewer Review the entire codebase focusing on:
- Python best practices
- Error handling
- Security issues
- Performance bottlenecks"
```

### Scenario 5: Redesign Web Interface
```
"@agent-ui-ux-designer Redesign the meeting assistant web interface with focus on:
- User research for meeting workflows
- Accessible transcription display
- Intuitive audio controls
- Mobile-responsive design"
```

### Scenario 6: Build Dashboard UI
```
"@agent-frontend-developer Build a real-time meeting dashboard using:
- WebSockets for live transcription
- React components for audio visualization
- Responsive layout with Tailwind CSS
- WCAG 2.1 AA accessibility"
```

### Scenario 7: Create Design System
```
"@agent-ui-designer Create a comprehensive design system for the web app:
- Color palette with dark mode
- Typography system
- Component library (buttons, forms, cards)
- Design tokens for consistency"
```

### Scenario 8: Validate UI Changes
```
"@agent-ui-visual-validator Validate the new dashboard implementation:
- Check WCAG 2.1 AA compliance
- Verify responsive breakpoints
- Test cross-browser compatibility
- Ensure design system consistency"
```

---

**Happy Coding with AI Agents! 🚀**
