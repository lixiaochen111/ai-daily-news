# One-Click Deployer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an Electron-based macOS desktop app that guides users through deploying AI Daily News to GitHub Pages via a 5-step wizard.

**Architecture:** Electron main process manages IPC and spawns Python subprocesses for deployment logic. Renderer process displays wizard UI using Tailwind CSS + vanilla JS. Python scripts handle git operations, GitHub API calls, and error diagnosis.

**Tech Stack:** Electron 30.x, Node.js 20.x, Python 3.11, Tailwind CSS 3.4, DaisyUI 4.x, GitPython, PyInstaller

---

## File Structure

### New Directory: `deployer/`

```
ai-daily-news/
└── deployer/                          # New Electron app
    ├── package.json                   # Electron dependencies
    ├── main.js                        # Electron main process
    ├── preload.js                     # IPC bridge
    ├── renderer/
    │   ├── index.html                # Single page app
    │   ├── style.css                 # Tailwind + custom styles
    │   └── app.js                    # Frontend logic
    ├── backend/
    │   ├── deploy.py                 # Main deployment script
    │   ├── validate.py               # Config validation
    │   ├── diagnose.py               # Error diagnosis
    │   └── github_api.py             # GitHub API wrapper
    ├── build/
    │   └── icon.icns                 # App icon
    └── dist/                          # Build output (gitignored)
```

---

## Task 1: Project Setup

**Files:**
- Create: `deployer/package.json`
- Create: `deployer/.gitignore`
- Create: `deployer/README.md`

- [ ] **Step 1: Create directory structure**

```bash
cd /Users/lixiaochen/Desktop/ai-daily-news
mkdir -p deployer/renderer deployer/backend deployer/build
```

- [ ] **Step 2: Initialize package.json**

Create `deployer/package.json`:

```json
{
  "name": "ai-daily-news-deployer",
  "version": "1.0.0",
  "description": "One-click deployer for AI Daily News",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dev": "electron . --dev",
    "build:python": "python3 build_backend.py",
    "build": "electron-builder --mac",
    "build:all": "npm run build:python && npm run build"
  },
  "keywords": ["electron", "ai-news", "deployer"],
  "author": "lixiaochen111",
  "license": "MIT",
  "devDependencies": {
    "electron": "^30.0.0",
    "electron-builder": "^24.13.0"
  },
  "dependencies": {},
  "build": {
    "appId": "com.ainews.deployer",
    "productName": "AI Daily News Deployer",
    "mac": {
      "category": "public.app-category.developer-tools",
      "icon": "build/icon.icns",
      "target": ["dmg", "zip"]
    },
    "files": [
      "main.js",
      "preload.js",
      "renderer/**/*",
      "backend/dist/**/*"
    ],
    "dmg": {
      "contents": [
        {
          "x": 130,
          "y": 220
        },
        {
          "x": 410,
          "y": 220,
          "type": "link",
          "path": "/Applications"
        }
      ]
    }
  }
}
```

- [ ] **Step 3: Create .gitignore**

Create `deployer/.gitignore`:

```
node_modules/
dist/
backend/dist/
backend/build/
*.pyc
__pycache__/
.DS_Store
```

- [ ] **Step 4: Create README**

Create `deployer/README.md`:

```markdown
# AI Daily News Deployer

Electron-based desktop app for one-click deployment of AI Daily News to GitHub Pages.

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build:all
```

Output: `dist/AI Daily News Deployer.dmg`
```

- [ ] **Step 5: Install dependencies**

```bash
cd deployer
npm install
```

Expected: electron and electron-builder installed

- [ ] **Step 6: Commit**

```bash
git add deployer/
git commit -m "feat(deployer): initialize Electron project structure"
```

---

## Task 2: Electron Main Process

**Files:**
- Create: `deployer/main.js`

- [ ] **Step 1: Create main.js skeleton**

Create `deployer/main.js`:

```javascript
const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  // Open DevTools in development mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC handlers (to be implemented)
```

- [ ] **Step 2: Test window creation**

```bash
cd deployer
npm run dev
```

Expected: Empty Electron window opens (800x600, non-resizable)

- [ ] **Step 3: Commit**

```bash
git add deployer/main.js
git commit -m "feat(deployer): add Electron main process with window creation"
```

---

## Task 3: Preload Script (IPC Bridge)

**Files:**
- Create: `deployer/preload.js`

- [ ] **Step 1: Create preload.js**

Create `deployer/preload.js`:

```javascript
const { contextBridge, ipcRenderer } = require('electron');

// Expose safe IPC methods to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Validation
  validateConfig: (step, data) => ipcRenderer.invoke('validate-config', step, data),
  testGitHubToken: (token) => ipcRenderer.invoke('test-github-token', token),
  
  // Deployment
  startDeploy: (config) => ipcRenderer.invoke('start-deploy', config),
  retryDeploy: () => ipcRenderer.invoke('retry-deploy'),
  
  // Utilities
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // Event listeners
  onDeployLog: (callback) => ipcRenderer.on('deploy-log', (event, message) => callback(message)),
  onDeployProgress: (callback) => ipcRenderer.on('deploy-progress', (event, progress) => callback(progress)),
  onDeploySuccess: (callback) => ipcRenderer.on('deploy-success', (event, result) => callback(result)),
  onDeployError: (callback) => ipcRenderer.on('deploy-error', (event, error) => callback(error))
});
```

- [ ] **Step 2: Verify preload loads**

Add to `deployer/main.js` after `app.whenReady()`:

```javascript
app.whenReady().then(() => {
  console.log('Preload script path:', path.join(__dirname, 'preload.js'));
  createWindow();
});
```

Run: `npm run dev`
Expected: Console logs preload path, no errors

- [ ] **Step 3: Commit**

```bash
git add deployer/preload.js deployer/main.js
git commit -m "feat(deployer): add preload script for secure IPC"
```

---

## Task 4: Frontend HTML Structure

**Files:**
- Create: `deployer/renderer/index.html`

- [ ] **Step 1: Create HTML skeleton**

Create `deployer/renderer/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; script-src 'self';">
  <title>AI Daily News Deployer</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.0.0/dist/full.css" rel="stylesheet">
  <link href="style.css" rel="stylesheet">
</head>
<body class="bg-base-200 h-screen overflow-hidden">
  <div id="app" class="h-full flex flex-col">
    <!-- Header -->
    <header class="bg-primary text-primary-content p-4">
      <h1 class="text-2xl font-bold">AI Daily News Deployer</h1>
      <p class="text-sm opacity-80">One-click deployment to GitHub Pages</p>
    </header>

    <!-- Progress Steps -->
    <div id="steps-indicator" class="bg-base-100 p-4 shadow-sm">
      <ul class="steps steps-horizontal w-full">
        <li class="step step-primary" data-step="1">Basic Info</li>
        <li class="step" data-step="2">GitHub Auth</li>
        <li class="step" data-step="3">RSS Feeds</li>
        <li class="step" data-step="4">Advanced</li>
        <li class="step" data-step="5">Deploy</li>
      </ul>
    </div>

    <!-- Main Content Area -->
    <main id="wizard-content" class="flex-1 overflow-y-auto p-6">
      <!-- Dynamic content loaded here -->
    </main>

    <!-- Footer Navigation -->
    <footer id="wizard-footer" class="bg-base-100 p-4 border-t flex justify-between">
      <button id="btn-back" class="btn btn-outline" style="display: none;">Back</button>
      <div class="flex-1"></div>
      <button id="btn-next" class="btn btn-primary">Next</button>
    </footer>
  </div>

  <!-- Hidden templates for each step -->
  <template id="step1-template">
    <div class="max-w-md mx-auto">
      <h2 class="text-xl font-bold mb-4">Basic Information</h2>
      <div class="form-control mb-4">
        <label class="label"><span class="label-text">GitHub Username *</span></label>
        <input type="text" id="github-username" class="input input-bordered" placeholder="lixiaochen111" required>
        <label class="label"><span class="label-text-alt text-error" id="error-username"></span></label>
      </div>
      <div class="form-control mb-4">
        <label class="label"><span class="label-text">Email Address *</span></label>
        <input type="email" id="email" class="input input-bordered" placeholder="you@example.com" required>
        <label class="label"><span class="label-text-alt text-error" id="error-email"></span></label>
      </div>
      <div class="form-control mb-4">
        <label class="label"><span class="label-text">Repository Name *</span></label>
        <input type="text" id="repo-name" class="input input-bordered" value="ai-daily-news" required>
        <label class="label"><span class="label-text-alt">Lowercase letters and hyphens only</span></label>
        <label class="label"><span class="label-text-alt text-error" id="error-repo"></span></label>
      </div>
    </div>
  </template>

  <template id="step2-template">
    <div class="max-w-md mx-auto">
      <h2 class="text-xl font-bold mb-4">GitHub Authentication</h2>
      <div class="alert alert-info mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span>Token must have 'repo' and 'workflow' permissions</span>
      </div>
      <div class="form-control mb-4">
        <label class="label"><span class="label-text">Personal Access Token *</span></label>
        <input type="password" id="github-token" class="input input-bordered font-mono" placeholder="ghp_..." required>
        <label class="label">
          <span class="label-text-alt">
            <a href="#" id="link-get-token" class="link link-primary">Get Token from GitHub</a>
          </span>
        </label>
        <label class="label"><span class="label-text-alt text-error" id="error-token"></span></label>
      </div>
      <div id="token-validation" class="hidden">
        <div class="alert alert-success">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span>Token validated successfully</span>
        </div>
      </div>
    </div>
  </template>

  <template id="step3-template">
    <div class="max-w-2xl mx-auto">
      <h2 class="text-xl font-bold mb-4">RSS Feed Configuration</h2>
      <div class="alert alert-info mb-4">
        <span>15 AI+Design Twitter accounts pre-configured. Add or remove feeds below.</span>
      </div>
      <div id="feeds-list" class="space-y-2 mb-4">
        <!-- Dynamically populated -->
      </div>
      <button id="btn-add-feed" class="btn btn-sm btn-outline">+ Add Custom Feed</button>
    </div>
  </template>

  <template id="step4-template">
    <div class="max-w-md mx-auto">
      <h2 class="text-xl font-bold mb-4">Advanced Options</h2>
      <div class="form-control mb-4">
        <label class="label"><span class="label-text">Update Frequency</span></label>
        <select id="update-frequency" class="select select-bordered">
          <option value="*/30 * * * *">Every 30 minutes</option>
          <option value="0 * * * *">Every hour</option>
          <option value="0 */6 * * *">Every 6 hours</option>
          <option value="0 2 * * *" selected>Daily at 10 AM Beijing Time</option>
        </select>
      </div>
      <div class="form-control mb-4">
        <label class="label"><span class="label-text">Timezone</span></label>
        <select id="timezone" class="select select-bordered">
          <option value="Asia/Shanghai" selected>Asia/Shanghai (Beijing)</option>
          <option value="UTC">UTC</option>
          <option value="America/New_York">America/New_York</option>
          <option value="Europe/London">Europe/London</option>
        </select>
      </div>
      <div class="divider">Optional Features</div>
      <div class="form-control mb-4">
        <label class="label cursor-pointer">
          <span class="label-text">Enable AgentMail Integration</span>
          <input type="checkbox" id="enable-agentmail" class="checkbox">
        </label>
      </div>
      <div id="agentmail-config" class="hidden ml-4 space-y-2">
        <input type="text" id="agentmail-api-key" class="input input-bordered input-sm w-full" placeholder="AgentMail API Key">
        <input type="text" id="agentmail-inbox-id" class="input input-bordered input-sm w-full" placeholder="Inbox ID">
      </div>
    </div>
  </template>

  <template id="step5-template">
    <div class="max-w-2xl mx-auto">
      <h2 class="text-xl font-bold mb-4">Review & Deploy</h2>
      <div id="config-summary" class="space-y-4 mb-6">
        <!-- Populated dynamically -->
      </div>
      <div id="deploy-area" class="hidden">
        <div class="mb-4">
          <progress id="deploy-progress" class="progress progress-primary w-full" value="0" max="100"></progress>
          <p id="deploy-phase" class="text-sm text-center mt-2">Ready to deploy...</p>
        </div>
        <div id="deploy-log" class="mockup-code bg-base-300 h-64 overflow-y-auto text-xs"></div>
      </div>
      <div id="deploy-success" class="hidden">
        <div class="alert alert-success mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span>Deployment successful!</span>
        </div>
        <div class="space-y-2">
          <a id="link-repo" href="#" class="btn btn-outline btn-sm w-full">View Repository</a>
          <a id="link-site" href="#" class="btn btn-outline btn-sm w-full">View Live Site</a>
          <a id="link-actions" href="#" class="btn btn-outline btn-sm w-full">Open GitHub Actions</a>
        </div>
      </div>
      <div id="deploy-error" class="hidden">
        <div class="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span id="error-message">Deployment failed</span>
        </div>
        <div class="collapse collapse-arrow bg-base-200">
          <input type="checkbox">
          <div class="collapse-title font-medium">Technical Details</div>
          <div class="collapse-content"><pre id="error-details" class="text-xs"></pre></div>
        </div>
        <div id="error-suggestions" class="mt-4">
          <p class="font-semibold mb-2">Suggested Actions:</p>
          <ul id="suggestions-list" class="list-disc list-inside space-y-1 text-sm"></ul>
        </div>
        <button id="btn-retry" class="btn btn-warning mt-4">Retry Deployment</button>
      </div>
    </div>
  </template>

  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Test HTML loads**

Run: `npm run dev`
Expected: Window shows header, step indicator, empty content area

- [ ] **Step 3: Commit**

```bash
git add deployer/renderer/index.html
git commit -m "feat(deployer): add HTML structure with 5-step wizard templates"
```

---

## Task 5: Frontend CSS Styling

**Files:**
- Create: `deployer/renderer/style.css`

- [ ] **Step 1: Create custom styles**

Create `deployer/renderer/style.css`:

```css
/* Custom styles for AI Daily News Deployer */

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

#wizard-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

/* Step indicator enhancements */
.steps .step-primary:before {
  background-color: #3b82f6;
  color: white;
}

/* Feed list item */
.feed-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--fallback-b1, oklch(var(--b1)));
  border: 1px solid var(--fallback-bc, oklch(var(--bc) / 0.2));
  border-radius: 0.5rem;
}

.feed-item input {
  flex: 1;
}

.feed-item button {
  flex-shrink: 0;
}

/* Deploy log styling */
#deploy-log {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

#deploy-log .log-info {
  color: #3b82f6;
}

#deploy-log .log-success {
  color: #10b981;
}

#deploy-log .log-error {
  color: #ef4444;
}

#deploy-log .log-warning {
  color: #f59e0b;
}

/* Config summary cards */
.config-card {
  padding: 1rem;
  background: var(--fallback-b1, oklch(var(--b1)));
  border: 1px solid var(--fallback-bc, oklch(var(--bc) / 0.2));
  border-radius: 0.5rem;
}

.config-card h3 {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.config-card p {
  font-size: 0.875rem;
  color: var(--fallback-bc, oklch(var(--bc) / 0.7));
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.step-content {
  animation: slideIn 0.3s ease-out;
}

/* Scrollbar styling */
#deploy-log::-webkit-scrollbar {
  width: 8px;
}

#deploy-log::-webkit-scrollbar-track {
  background: var(--fallback-b2, oklch(var(--b2)));
}

#deploy-log::-webkit-scrollbar-thumb {
  background: var(--fallback-bc, oklch(var(--bc) / 0.3));
  border-radius: 4px;
}

#deploy-log::-webkit-scrollbar-thumb:hover {
  background: var(--fallback-bc, oklch(var(--bc) / 0.5));
}
```

- [ ] **Step 2: Test styling**

Run: `npm run dev`
Expected: Styled UI with proper layout, colors, and spacing

- [ ] **Step 3: Commit**

```bash
git add deployer/renderer/style.css
git commit -m "feat(deployer): add custom CSS styling for wizard UI"
```

---

## Task 6: Frontend JavaScript - Wizard Logic

**Files:**
- Create: `deployer/renderer/app.js`

- [ ] **Step 1: Create app.js with wizard state management**

Create `deployer/renderer/app.js`:

```javascript
// Global state
const state = {
  currentStep: 1,
  config: {
    github: { username: '', email: '', repoName: 'ai-daily-news' },
    token: '',
    feeds: [],
    schedule: { cron: '0 2 * * *', timezone: 'Asia/Shanghai' },
    advanced: { agentmailEnabled: false, agentmailApiKey: '', agentmailInboxId: '' }
  }
};

// DOM elements
const elements = {
  stepsIndicator: document.getElementById('steps-indicator'),
  wizardContent: document.getElementById('wizard-content'),
  wizardFooter: document.getElementById('wizard-footer'),
  btnBack: document.getElementById('btn-back'),
  btnNext: document.getElementById('btn-next')
};

// Initialize app
function init() {
  loadDefaultFeeds();
  renderStep(1);
  setupEventListeners();
}

// Load default feeds from example OPML
function loadDefaultFeeds() {
  state.config.feeds = [
    { title: 'Sam Altman', url: 'https://nitter.net/sama/rss', category: 'AI Leaders' },
    { title: 'Anthropic', url: 'https://nitter.net/AnthropicAI/rss', category: 'AI Companies' },
    { title: 'OpenAI', url: 'https://nitter.net/OpenAI/rss', category: 'AI Companies' },
    { title: 'Google DeepMind', url: 'https://nitter.net/GoogleDeepMind/rss', category: 'AI Companies' },
    { title: 'Hugging Face', url: 'https://nitter.net/huggingface/rss', category: 'AI Companies' },
    { title: 'Andrej Karpathy', url: 'https://nitter.net/karpathy/rss', category: 'AI Researchers' },
    { title: 'Yann LeCun', url: 'https://nitter.net/ylecun/rss', category: 'AI Researchers' },
    { title: 'Greg Brockman', url: 'https://nitter.net/gdb/rss', category: 'AI Leaders' },
    { title: 'Demis Hassabis', url: 'https://nitter.net/demishassabis/rss', category: 'AI Leaders' },
    { title: 'Dario Amodei', url: 'https://nitter.net/darioamodei/rss', category: 'AI Leaders' },
    { title: 'AI Breakfast', url: 'https://aibreakfast.beehiiv.com/feed', category: 'Newsletters' },
    { title: 'GitHub AI', url: 'https://github.blog/ai/feed/', category: 'Developer Tools' },
    { title: 'Vercel AI', url: 'https://vercel.com/blog/ai/rss.xml', category: 'Developer Tools' },
    { title: 'Figma', url: 'https://nitter.net/figma/rss', category: 'Design' },
    { title: 'Adobe', url: 'https://nitter.net/Adobe/rss', category: 'Design' }
  ];
}

// Render specific step
function renderStep(step) {
  state.currentStep = step;
  updateStepsIndicator();
  updateNavigationButtons();

  const template = document.getElementById(`step${step}-template`);
  elements.wizardContent.innerHTML = '';
  const content = template.content.cloneNode(true);
  content.firstElementChild.classList.add('step-content');
  elements.wizardContent.appendChild(content);

  // Step-specific initialization
  switch(step) {
    case 1: initStep1(); break;
    case 2: initStep2(); break;
    case 3: initStep3(); break;
    case 4: initStep4(); break;
    case 5: initStep5(); break;
  }
}

// Update steps indicator
function updateStepsIndicator() {
  const steps = elements.stepsIndicator.querySelectorAll('.step');
  steps.forEach((step, index) => {
    if (index < state.currentStep) {
      step.classList.add('step-primary');
    } else {
      step.classList.remove('step-primary');
    }
  });
}

// Update navigation buttons
function updateNavigationButtons() {
  elements.btnBack.style.display = state.currentStep > 1 ? 'inline-flex' : 'none';
  
  if (state.currentStep === 5) {
    elements.btnNext.textContent = 'Deploy';
    elements.btnNext.classList.remove('btn-primary');
    elements.btnNext.classList.add('btn-success');
  } else {
    elements.btnNext.textContent = 'Next';
    elements.btnNext.classList.remove('btn-success');
    elements.btnNext.classList.add('btn-primary');
  }
}

// Setup event listeners
function setupEventListeners() {
  elements.btnBack.addEventListener('click', () => {
    if (state.currentStep > 1) {
      renderStep(state.currentStep - 1);
    }
  });

  elements.btnNext.addEventListener('click', async () => {
    if (await validateCurrentStep()) {
      if (state.currentStep < 5) {
        renderStep(state.currentStep + 1);
      } else {
        startDeployment();
      }
    }
  });
}

// Validate current step
async function validateCurrentStep() {
  switch(state.currentStep) {
    case 1: return validateStep1();
    case 2: return await validateStep2();
    case 3: return validateStep3();
    case 4: return validateStep4();
    case 5: return true;
    default: return true;
  }
}

// Step 1: Basic Info
function initStep1() {
  const usernameInput = document.getElementById('github-username');
  const emailInput = document.getElementById('email');
  const repoInput = document.getElementById('repo-name');

  usernameInput.value = state.config.github.username;
  emailInput.value = state.config.github.email;
  repoInput.value = state.config.github.repoName;

  [usernameInput, emailInput, repoInput].forEach(input => {
    input.addEventListener('input', () => {
      state.config.github[input.id.replace('github-', '').replace('repo-name', 'repoName')] = input.value;
    });
  });
}

function validateStep1() {
  let valid = true;
  const username = document.getElementById('github-username').value.trim();
  const email = document.getElementById('email').value.trim();
  const repoName = document.getElementById('repo-name').value.trim();

  // Clear previous errors
  document.getElementById('error-username').textContent = '';
  document.getElementById('error-email').textContent = '';
  document.getElementById('error-repo').textContent = '';

  if (!username || !/^[a-zA-Z0-9-]+$/.test(username)) {
    document.getElementById('error-username').textContent = 'Invalid username format';
    valid = false;
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    document.getElementById('error-email').textContent = 'Invalid email format';
    valid = false;
  }

  if (!repoName || !/^[a-z0-9-]+$/.test(repoName)) {
    document.getElementById('error-repo').textContent = 'Use lowercase letters and hyphens only';
    valid = false;
  }

  if (valid) {
    state.config.github = { username, email, repoName };
  }

  return valid;
}

// Step 2: GitHub Auth
function initStep2() {
  const tokenInput = document.getElementById('github-token');
  const getLinkButton = document.getElementById('link-get-token');

  tokenInput.value = state.config.token;
  tokenInput.addEventListener('input', () => {
    state.config.token = tokenInput.value;
    document.getElementById('token-validation').classList.add('hidden');
  });

  getLinkButton.addEventListener('click', (e) => {
    e.preventDefault();
    window.electronAPI.openExternal('https://github.com/settings/tokens/new?description=AI%20Daily%20News%20Deployer&scopes=repo,workflow');
  });
}

async function validateStep2() {
  const token = document.getElementById('github-token').value.trim();
  document.getElementById('error-token').textContent = '';

  if (!token) {
    document.getElementById('error-token').textContent = 'Token is required';
    return false;
  }

  // Test token validity
  try {
    elements.btnNext.disabled = true;
    elements.btnNext.innerHTML = '<span class="loading loading-spinner"></span> Validating...';
    
    const result = await window.electronAPI.testGitHubToken(token);
    
    if (result.valid) {
      document.getElementById('token-validation').classList.remove('hidden');
      state.config.token = token;
      return true;
    } else {
      document.getElementById('error-token').textContent = result.error || 'Invalid token';
      return false;
    }
  } catch (error) {
    document.getElementById('error-token').textContent = 'Failed to validate token';
    return false;
  } finally {
    elements.btnNext.disabled = false;
    elements.btnNext.textContent = 'Next';
  }
}

// Step 3: RSS Feeds
function initStep3() {
  renderFeedsList();
  
  document.getElementById('btn-add-feed').addEventListener('click', () => {
    state.config.feeds.push({ title: '', url: '', category: 'Custom' });
    renderFeedsList();
  });
}

function renderFeedsList() {
  const feedsList = document.getElementById('feeds-list');
  feedsList.innerHTML = '';

  state.config.feeds.forEach((feed, index) => {
    const feedItem = document.createElement('div');
    feedItem.className = 'feed-item';
    feedItem.innerHTML = `
      <input type="text" class="input input-sm input-bordered flex-1" placeholder="Feed Title" value="${feed.title}" data-index="${index}" data-field="title">
      <input type="text" class="input input-sm input-bordered flex-1" placeholder="Feed URL" value="${feed.url}" data-index="${index}" data-field="url">
      <button class="btn btn-sm btn-error btn-outline" data-index="${index}">Remove</button>
    `;
    feedsList.appendChild(feedItem);
  });

  // Add event listeners
  feedsList.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', (e) => {
      const index = parseInt(e.target.dataset.index);
      const field = e.target.dataset.field;
      state.config.feeds[index][field] = e.target.value;
    });
  });

  feedsList.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', (e) => {
      const index = parseInt(e.target.dataset.index);
      state.config.feeds.splice(index, 1);
      renderFeedsList();
    });
  });
}

function validateStep3() {
  // Feeds are optional, but if provided should have valid URLs
  const invalidFeeds = state.config.feeds.filter(f => f.url && !isValidUrl(f.url));
  if (invalidFeeds.length > 0) {
    alert('Some feed URLs are invalid. Please correct them.');
    return false;
  }
  return true;
}

function isValidUrl(string) {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}

// Step 4: Advanced Options
function initStep4() {
  const frequencySelect = document.getElementById('update-frequency');
  const timezoneSelect = document.getElementById('timezone');
  const agentmailCheckbox = document.getElementById('enable-agentmail');
  const agentmailConfig = document.getElementById('agentmail-config');

  frequencySelect.value = state.config.schedule.cron;
  timezoneSelect.value = state.config.schedule.timezone;
  agentmailCheckbox.checked = state.config.advanced.agentmailEnabled;
  agentmailConfig.classList.toggle('hidden', !agentmailCheckbox.checked);

  frequencySelect.addEventListener('change', () => {
    state.config.schedule.cron = frequencySelect.value;
  });

  timezoneSelect.addEventListener('change', () => {
    state.config.schedule.timezone = timezoneSelect.value;
  });

  agentmailCheckbox.addEventListener('change', () => {
    state.config.advanced.agentmailEnabled = agentmailCheckbox.checked;
    agentmailConfig.classList.toggle('hidden', !agentmailCheckbox.checked);
  });

  document.getElementById('agentmail-api-key').addEventListener('input', (e) => {
    state.config.advanced.agentmailApiKey = e.target.value;
  });

  document.getElementById('agentmail-inbox-id').addEventListener('input', (e) => {
    state.config.advanced.agentmailInboxId = e.target.value;
  });
}

function validateStep4() {
  if (state.config.advanced.agentmailEnabled) {
    if (!state.config.advanced.agentmailApiKey || !state.config.advanced.agentmailInboxId) {
      alert('AgentMail integration requires both API Key and Inbox ID');
      return false;
    }
  }
  return true;
}

// Step 5: Review & Deploy
function initStep5() {
  renderConfigSummary();
  
  // Hide deploy UI initially
  document.getElementById('deploy-area').classList.add('hidden');
  document.getElementById('deploy-success').classList.add('hidden');
  document.getElementById('deploy-error').classList.add('hidden');
  
  // Change Next button to Deploy
  elements.btnNext.textContent = 'Deploy';
  elements.btnNext.classList.remove('btn-primary');
  elements.btnNext.classList.add('btn-success');
}

function renderConfigSummary() {
  const summaryDiv = document.getElementById('config-summary');
  const { github, feeds, schedule, advanced } = state.config;
  
  summaryDiv.innerHTML = `
    <div class="config-card">
      <h3>GitHub Configuration</h3>
      <p><strong>Username:</strong> ${github.username}</p>
      <p><strong>Email:</strong> ${github.email}</p>
      <p><strong>Repository:</strong> ${github.repoName}</p>
    </div>
    <div class="config-card">
      <h3>RSS Feeds</h3>
      <p><strong>Feed Count:</strong> ${feeds.length} sources</p>
    </div>
    <div class="config-card">
      <h3>Update Schedule</h3>
      <p><strong>Frequency:</strong> ${getCronDescription(schedule.cron)}</p>
      <p><strong>Timezone:</strong> ${schedule.timezone}</p>
    </div>
    <div class="config-card">
      <h3>Advanced Features</h3>
      <p><strong>AgentMail:</strong> ${advanced.agentmailEnabled ? 'Enabled' : 'Disabled'}</p>
    </div>
  `;
}

function getCronDescription(cron) {
  const descriptions = {
    '*/30 * * * *': 'Every 30 minutes',
    '0 * * * *': 'Every hour',
    '0 */6 * * *': 'Every 6 hours',
    '0 2 * * *': 'Daily at 10 AM Beijing Time'
  };
  return descriptions[cron] || cron;
}

// Start deployment
async function startDeployment() {
  // Show deploy area
  document.getElementById('config-summary').classList.add('hidden');
  document.getElementById('deploy-area').classList.remove('hidden');
  elements.btnNext.disabled = true;
  elements.btnBack.disabled = true;

  // Setup log listeners
  window.electronAPI.onDeployLog((message) => {
    appendLog(message.text, message.level);
  });

  window.electronAPI.onDeployProgress((progress) => {
    updateProgress(progress);
  });

  window.electronAPI.onDeploySuccess((result) => {
    showSuccess(result);
  });

  window.electronAPI.onDeployError((error) => {
    showError(error);
  });

  // Start deployment
  try {
    await window.electronAPI.startDeploy(state.config);
  } catch (error) {
    showError({ message: error.message, details: error.stack });
  }
}

function appendLog(text, level = 'info') {
  const logDiv = document.getElementById('deploy-log');
  const line = document.createElement('div');
  line.className = `log-${level}`;
  line.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
  logDiv.appendChild(line);
  logDiv.scrollTop = logDiv.scrollHeight;
}

function updateProgress(progress) {
  const progressBar = document.getElementById('deploy-progress');
  const phaseText = document.getElementById('deploy-phase');
  progressBar.value = progress.percent;
  phaseText.textContent = progress.phase;
}

function showSuccess(result) {
  document.getElementById('deploy-area').classList.add('hidden');
  document.getElementById('deploy-success').classList.remove('hidden');
  
  const { username, repoName } = state.config.github;
  document.getElementById('link-repo').href = `https://github.com/${username}/${repoName}`;
  document.getElementById('link-site').href = `https://${username}.github.io/${repoName}`;
  document.getElementById('link-actions').href = `https://github.com/${username}/${repoName}/actions`;
  
  // Update button to "Done"
  elements.btnNext.textContent = 'Done';
  elements.btnNext.disabled = false;
  elements.btnNext.onclick = () => window.close();
  
  // Add external link handlers
  ['link-repo', 'link-site', 'link-actions'].forEach(id => {
    document.getElementById(id).addEventListener('click', (e) => {
      e.preventDefault();
      window.electronAPI.openExternal(e.target.href);
    });
  });
}

function showError(error) {
  document.getElementById('deploy-area').classList.add('hidden');
  document.getElementById('deploy-error').classList.remove('hidden');
  
  document.getElementById('error-message').textContent = error.message;
  document.getElementById('error-details').textContent = error.details || 'No additional details';
  
  const suggestionsList = document.getElementById('suggestions-list');
  suggestionsList.innerHTML = '';
  (error.suggestions || []).forEach(suggestion => {
    const li = document.createElement('li');
    li.textContent = suggestion;
    suggestionsList.appendChild(li);
  });
  
  document.getElementById('btn-retry').addEventListener('click', async () => {
    document.getElementById('deploy-error').classList.add('hidden');
    document.getElementById('deploy-area').classList.remove('hidden');
    await window.electronAPI.retryDeploy();
  });
  
  elements.btnNext.disabled = false;
  elements.btnBack.disabled = false;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
```

- [ ] **Step 2: Test wizard navigation**

Run: `npm run dev`
Expected: Can navigate through all 5 steps, forms work, validation triggers

- [ ] **Step 3: Commit**

```bash
git add deployer/renderer/app.js
git commit -m "feat(deployer): add frontend wizard logic and state management"
```

---

## Task 7: Python Backend - Validation Script

**Files:**
- Create: `deployer/backend/validate.py`

- [ ] **Step 1: Create validate.py**

Create `deployer/backend/validate.py`:

```python
#!/usr/bin/env python3
"""Configuration validation for AI Daily News deployer."""

import re
import sys
import json
import requests
from typing import Dict, List, Tuple

def validate_github_username(username: str) -> Tuple[bool, str]:
    """Validate GitHub username format."""
    if not username:
        return False, "Username is required"
    if not re.match(r'^[a-zA-Z0-9-]+$', username):
        return False, "Username can only contain letters, numbers, and hyphens"
    if len(username) > 39:
        return False, "Username is too long (max 39 characters)"
    return True, ""

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format."""
    if not email:
        return False, "Email is required"
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""

def validate_repo_name(repo_name: str) -> Tuple[bool, str]:
    """Validate repository name format."""
    if not repo_name:
        return False, "Repository name is required"
    if not re.match(r'^[a-z0-9-]+$', repo_name):
        return False, "Repository name must use lowercase letters, numbers, and hyphens only"
    if len(repo_name) > 100:
        return False, "Repository name is too long (max 100 characters)"
    return True, ""

def validate_github_token(token: str) -> Tuple[bool, str]:
    """Validate GitHub token by making an API call."""
    if not token:
        return False, "Token is required"
    
    if not token.startswith(('ghp_', 'github_pat_')):
        return False, "Token format appears invalid"
    
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Check scopes
            scopes = response.headers.get('X-OAuth-Scopes', '').split(', ')
            required_scopes = {'repo', 'workflow'}
            missing = required_scopes - set(scopes)
            if missing:
                return False, f"Token missing required scopes: {', '.join(missing)}"
            return True, ""
        elif response.status_code == 401:
            return False, "Token is invalid or expired"
        elif response.status_code == 403:
            return False, "Token has insufficient permissions"
        else:
            return False, f"Unexpected response: {response.status_code}"
    except requests.RequestException as e:
        return False, f"Network error: {str(e)}"

def validate_feed_url(url: str) -> Tuple[bool, str]:
    """Validate RSS feed URL format."""
    if not url:
        return True, ""  # Empty URLs are ok (feed is optional)
    
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        if result.scheme not in ['http', 'https']:
            return False, "URL must use http or https"
        return True, ""
    except Exception:
        return False, "Invalid URL"

def validate_cron(cron: str) -> Tuple[bool, str]:
    """Validate cron expression format."""
    if not cron:
        return False, "Cron expression is required"
    
    parts = cron.split()
    if len(parts) != 5:
        return False, "Cron expression must have 5 parts"
    
    # Basic validation (not exhaustive)
    return True, ""

def main():
    """Main validation entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"valid": False, "error": "No validation type specified"}))
        sys.exit(1)
    
    validation_type = sys.argv[1]
    data = sys.argv[2] if len(sys.argv) > 2 else ""
    
    result = {"valid": False, "error": "Unknown validation type"}
    
    if validation_type == "username":
        valid, error = validate_github_username(data)
        result = {"valid": valid, "error": error}
    elif validation_type == "email":
        valid, error = validate_email(data)
        result = {"valid": valid, "error": error}
    elif validation_type == "repo_name":
        valid, error = validate_repo_name(data)
        result = {"valid": valid, "error": error}
    elif validation_type == "github_token":
        valid, error = validate_github_token(data)
        result = {"valid": valid, "error": error}
    elif validation_type == "feed_url":
        valid, error = validate_feed_url(data)
        result = {"valid": valid, "error": error}
    elif validation_type == "cron":
        valid, error = validate_cron(data)
        result = {"valid": valid, "error": error}
    
    print(json.dumps(result))
    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write test for validation**

Create `deployer/backend/test_validate.py`:

```python
#!/usr/bin/env python3
"""Tests for validation script."""

import subprocess
import json

def test_validate_username():
    """Test username validation."""
    # Valid
    result = subprocess.run(['python3', 'validate.py', 'username', 'lixiaochen111'], 
                          capture_output=True, text=True)
    data = json.loads(result.stdout)
    assert data['valid'] == True
    
    # Invalid
    result = subprocess.run(['python3', 'validate.py', 'username', 'invalid@name'], 
                          capture_output=True, text=True)
    data = json.loads(result.stdout)
    assert data['valid'] == False

def test_validate_email():
    """Test email validation."""
    # Valid
    result = subprocess.run(['python3', 'validate.py', 'email', 'test@example.com'], 
                          capture_output=True, text=True)
    data = json.loads(result.stdout)
    assert data['valid'] == True
    
    # Invalid
    result = subprocess.run(['python3', 'validate.py', 'email', 'invalid-email'], 
                          capture_output=True, text=True)
    data = json.loads(result.stdout)
    assert data['valid'] == False

if __name__ == '__main__':
    test_validate_username()
    test_validate_email()
    print("✓ All validation tests passed")
```

- [ ] **Step 3: Run tests**

```bash
cd deployer/backend
python3 test_validate.py
```

Expected: "✓ All validation tests passed"

- [ ] **Step 4: Commit**

```bash
git add deployer/backend/validate.py deployer/backend/test_validate.py
git commit -m "feat(deployer): add Python validation script with tests"
```

---

## Task 8: Python Backend - GitHub API Wrapper

**Files:**
- Create: `deployer/backend/github_api.py`

- [ ] **Step 1: Create github_api.py**

Create `deployer/backend/github_api.py`:

```python
#!/usr/bin/env python3
"""GitHub API wrapper for deployment operations."""

import requests
import time
from typing import Dict, Optional

class GitHubAPI:
    """GitHub API client."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_user(self) -> Dict:
        """Get authenticated user info."""
        response = requests.get(f"{self.base_url}/user", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def check_repo_exists(self, owner: str, repo: str) -> bool:
        """Check if repository exists."""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        return response.status_code == 200
    
    def create_repo(self, name: str, description: str = "", private: bool = False) -> Dict:
        """Create a new repository."""
        data = {
            'name': name,
            'description': description,
            'private': private,
            'auto_init': False
        }
        response = requests.post(
            f"{self.base_url}/user/repos",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def enable_pages(self, owner: str, repo: str, branch: str = "main") -> Dict:
        """Enable GitHub Pages."""
        data = {
            'source': {
                'branch': branch,
                'path': '/'
            }
        }
        response = requests.post(
            f"{self.base_url}/repos/{owner}/{repo}/pages",
            headers=self.headers,
            json=data
        )
        
        # 409 means pages already enabled
        if response.status_code == 409:
            return {'status': 'already_enabled'}
        
        response.raise_for_status()
        return response.json()
    
    def trigger_workflow(self, owner: str, repo: str, workflow_id: str, ref: str = "main") -> Dict:
        """Trigger a GitHub Actions workflow."""
        data = {'ref': ref}
        response = requests.post(
            f"{self.base_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return {'status': 'triggered'}
    
    def get_workflow_runs(self, owner: str, repo: str, workflow_id: str) -> Dict:
        """Get workflow runs."""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_pages(self, owner: str, repo: str, timeout: int = 60) -> bool:
        """Wait for GitHub Pages to become available."""
        start_time = time.time()
        pages_url = f"https://{owner}.github.io/{repo}/"
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(pages_url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(5)
        
        return False
```

- [ ] **Step 2: Test GitHub API wrapper**

Create `deployer/backend/test_github_api.py`:

```python
#!/usr/bin/env python3
"""Tests for GitHub API wrapper (requires valid token)."""

import os
from github_api import GitHubAPI

def test_get_user():
    """Test getting user info."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("⊘ Skipping test (no GITHUB_TOKEN set)")
        return
    
    api = GitHubAPI(token)
    user = api.get_user()
    assert 'login' in user
    print(f"✓ Authenticated as: {user['login']}")

if __name__ == '__main__':
    test_get_user()
    print("✓ GitHub API tests passed")
```

- [ ] **Step 3: Run test (optional, needs token)**

```bash
cd deployer/backend
export GITHUB_TOKEN=your_test_token
python3 test_github_api.py
```

Expected: "✓ Authenticated as: <username>" or skip message

- [ ] **Step 4: Commit**

```bash
git add deployer/backend/github_api.py deployer/backend/test_github_api.py
git commit -m "feat(deployer): add GitHub API wrapper for deployment operations"
```

---

## Task 9: Python Backend - Deploy Script

**Files:**
- Create: `deployer/backend/deploy.py`

- [ ] **Step 1: Create deploy.py**

Create `deployer/backend/deploy.py`:

```python
#!/usr/bin/env python3
"""Main deployment script for AI Daily News."""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict
from github_api import GitHubAPI

class DeploymentError(Exception):
    """Deployment error with exit code."""
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code

def log(message: str, level: str = "info"):
    """Log message to stdout in JSON format."""
    print(json.dumps({"text": message, "level": level}), flush=True)

def progress(percent: int, phase: str):
    """Report progress."""
    print(json.dumps({"type": "progress", "percent": percent, "phase": phase}), flush=True)

def run_command(cmd: list, cwd: str = None) -> subprocess.CompletedProcess:
    """Run shell command and return result."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Command failed: {' '.join(cmd)}", "error")
        log(f"Error: {result.stderr}", "error")
        raise DeploymentError(f"Command failed: {result.stderr}", exit_code=2)
    return result

def validate_prerequisites():
    """Validate required tools are available."""
    log("Validating prerequisites...")
    
    # Check git
    try:
        run_command(['git', '--version'])
        log("✓ Git is available", "success")
    except Exception:
        raise DeploymentError("Git is not installed", exit_code=10)
    
    # Check python
    try:
        run_command(['python3', '--version'])
        log("✓ Python is available", "success")
    except Exception:
        raise DeploymentError("Python 3 is not installed", exit_code=11)

def configure_git(config: Dict):
    """Configure git with user info."""
    log("Configuring Git...")
    username = config['github']['username']
    email = config['github']['email']
    
    run_command(['git', 'config', '--global', 'user.name', username])
    run_command(['git', 'config', '--global', 'user.email', email])
    log(f"✓ Git configured for {username} <{email}>", "success")

def prepare_repository(config: Dict) -> str:
    """Prepare ai-daily-news repository."""
    log("Preparing repository...")
    progress(20, "Cloning ai-daily-news repository...")
    
    # Determine project root (assuming this script is in deployer/backend/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # Go up two levels
    ai_news_dir = project_root / 'ai-daily-news'
    
    # Check if ai-daily-news directory exists
    if not ai_news_dir.exists():
        raise DeploymentError(
            f"AI Daily News directory not found at {ai_news_dir}",
            exit_code=20
        )
    
    log(f"✓ Found ai-daily-news at {ai_news_dir}", "success")
    
    # Configure OPML
    feeds = config.get('feeds', [])
    if feeds:
        log(f"Configuring {len(feeds)} RSS feeds...")
        generate_opml(ai_news_dir / 'feeds' / 'follow.opml', feeds)
    
    # Configure workflow schedule
    schedule = config.get('schedule', {})
    if schedule:
        log("Updating workflow schedule...")
        update_workflow_schedule(
            ai_news_dir / '.github' / 'workflows' / 'update-news.yml',
            schedule['cron']
        )
    
    return str(ai_news_dir)

def generate_opml(opml_path: Path, feeds: list):
    """Generate OPML file from feeds list."""
    opml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head>
    <title>AI Daily News Feeds</title>
  </head>
  <body>
'''
    
    # Group by category
    categories = {}
    for feed in feeds:
        cat = feed.get('category', 'Uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(feed)
    
    for category, cat_feeds in categories.items():
        opml_content += f'    <outline text="{category}">\n'
        for feed in cat_feeds:
            title = feed.get('title', '')
            url = feed.get('url', '')
            opml_content += f'      <outline type="rss" text="{title}" xmlUrl="{url}"/>\n'
        opml_content += '    </outline>\n'
    
    opml_content += '''  </body>
</opml>'''
    
    opml_path.parent.mkdir(parents=True, exist_ok=True)
    opml_path.write_text(opml_content)
    log(f"✓ Generated OPML with {len(feeds)} feeds", "success")

def update_workflow_schedule(workflow_path: Path, cron: str):
    """Update GitHub Actions workflow schedule."""
    content = workflow_path.read_text()
    
    # Replace cron expression (simple regex replacement)
    import re
    new_content = re.sub(
        r'cron:\s*"[^"]*"',
        f'cron: "{cron}"',
        content
    )
    
    workflow_path.write_text(new_content)
    log(f"✓ Updated workflow schedule to: {cron}", "success")

def push_to_github(config: Dict, repo_dir: str):
    """Push repository to GitHub."""
    log("Pushing to GitHub...")
    progress(40, "Configuring remote repository...")
    
    username = config['github']['username']
    repo_name = config['github']['repoName']
    token = config['token']
    
    # Remove existing origin
    try:
        run_command(['git', 'remote', 'remove', 'origin'], cwd=repo_dir)
    except Exception:
        pass  # Origin may not exist
    
    # Add new origin with token
    remote_url = f'https://{token}@github.com/{username}/{repo_name}.git'
    run_command(['git', 'remote', 'add', 'origin', remote_url], cwd=repo_dir)
    log("✓ Remote configured", "success")
    
    # Add, commit, push
    progress(50, "Committing changes...")
    run_command(['git', 'add', '.'], cwd=repo_dir)
    try:
        run_command([
            'git', 'commit', '-m',
            'feat: customize AI Daily News configuration\n\nDeployed via AI Daily News Deployer'
        ], cwd=repo_dir)
    except DeploymentError:
        log("No changes to commit", "info")
    
    progress(60, "Pushing to GitHub...")
    run_command(['git', 'branch', '-M', 'main'], cwd=repo_dir)
    run_command(['git', 'push', '-u', 'origin', 'main', '--force'], cwd=repo_dir)
    log("✓ Pushed to GitHub", "success")

def configure_github_actions(config: Dict):
    """Configure GitHub Actions and Pages."""
    log("Configuring GitHub Actions...")
    progress(70, "Setting up GitHub Actions...")
    
    username = config['github']['username']
    repo_name = config['github']['repoName']
    token = config['token']
    
    api = GitHubAPI(token)
    
    # Check repository exists
    if not api.check_repo_exists(username, repo_name):
        log(f"Creating repository {username}/{repo_name}...", "info")
        api.create_repo(repo_name, description="AI Daily News - Automated news aggregator")
    
    log("✓ Repository confirmed", "success")

def enable_github_pages(config: Dict):
    """Enable GitHub Pages."""
    log("Enabling GitHub Pages...")
    progress(80, "Enabling GitHub Pages...")
    
    username = config['github']['username']
    repo_name = config['github']['repoName']
    token = config['token']
    
    api = GitHubAPI(token)
    
    try:
        result = api.enable_pages(username, repo_name, branch='main')
        if result.get('status') == 'already_enabled':
            log("✓ GitHub Pages already enabled", "success")
        else:
            log("✓ GitHub Pages enabled", "success")
    except Exception as e:
        log(f"GitHub Pages setup: {str(e)}", "warning")
        log("You may need to enable Pages manually in repository settings", "info")

def verify_deployment(config: Dict):
    """Verify deployment success."""
    log("Verifying deployment...")
    progress(90, "Verifying deployment...")
    
    username = config['github']['username']
    repo_name = config['github']['repoName']
    
    log(f"✓ Repository: https://github.com/{username}/{repo_name}", "success")
    log(f"✓ Live site: https://{username}.github.io/{repo_name}/", "success")
    log(f"✓ Actions: https://github.com/{username}/{repo_name}/actions", "success")
    
    progress(100, "Deployment complete!")

def main():
    """Main deployment entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No configuration provided"}))
        sys.exit(1)
    
    try:
        config = json.loads(sys.argv[1])
        
        progress(0, "Starting deployment...")
        validate_prerequisites()
        
        progress(10, "Configuring Git...")
        configure_git(config)
        
        repo_dir = prepare_repository(config)
        push_to_github(config, repo_dir)
        configure_github_actions(config)
        enable_github_pages(config)
        verify_deployment(config)
        
        log("✓ Deployment successful!", "success")
        print(json.dumps({"type": "success", "username": config['github']['username'], "repoName": config['github']['repoName']}))
        sys.exit(0)
        
    except DeploymentError as e:
        log(f"Deployment failed: {str(e)}", "error")
        print(json.dumps({"type": "error", "message": str(e), "exit_code": e.exit_code}))
        sys.exit(e.exit_code)
    except Exception as e:
        log(f"Unexpected error: {str(e)}", "error")
        print(json.dumps({"type": "error", "message": str(e), "exit_code": 1}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create requirements file for Python backend**

Create `deployer/backend/requirements.txt`:

```
requests>=2.31.0
```

- [ ] **Step 3: Test deploy script structure (without actual deployment)**

```bash
cd deployer/backend
pip3 install -r requirements.txt
echo '{}' | python3 deploy.py
```

Expected: Error message about missing configuration (script loads correctly)

- [ ] **Step 4: Commit**

```bash
git add deployer/backend/deploy.py deployer/backend/requirements.txt
git commit -m "feat(deployer): add main deployment script with phased execution"
```

---

## Task 10: Python Backend - Diagnosis Script

**Files:**
- Create: `deployer/backend/diagnose.py`

- [ ] **Step 1: Create diagnose.py**

Create `deployer/backend/diagnose.py`:

```python
#!/usr/bin/env python3
"""Error diagnosis for deployment failures."""

import sys
import json
import re
from typing import Dict, List

ERROR_PATTERNS = {
    'network': {
        'patterns': [
            r'Connection.*timeout',
            r'Network.*unreachable',
            r'DNS.*failed',
            r'Could not resolve host'
        ],
        'suggestions': [
            'Check your internet connection',
            'Disable VPN or proxy temporarily',
            'Try again in a few minutes',
            'Check firewall settings'
        ]
    },
    'authentication': {
        'patterns': [
            r'401.*Unauthorized',
            r'403.*Forbidden',
            r'Bad credentials',
            r'Invalid.*token'
        ],
        'suggestions': [
            'Verify your Personal Access Token is correct',
            'Ensure token has repo and workflow permissions',
            'Token may have expired - generate a new one',
            'Check if 2FA is enabled on your GitHub account'
        ]
    },
    'repository': {
        'patterns': [
            r'Repository.*already exists',
            r'Permission denied',
            r'Repository not found'
        ],
        'suggestions': [
            'Repository name may be taken - try a different name',
            'You may not have permission to create repositories',
            'For existing repos, the deployment will update it'
        ]
    },
    'git': {
        'patterns': [
            r'fatal:.*git',
            r'Author identity unknown',
            r'refusing to merge'
        ],
        'suggestions': [
            'Verify your email address is correct',
            'Check git is installed properly',
            'Try running the deployment again'
        ]
    },
    'python': {
        'patterns': [
            r'ModuleNotFoundError',
            r'ImportError',
            r'No module named'
        ],
        'suggestions': [
            'Python dependencies may be missing',
            'Try reinstalling the application',
            'Check disk space availability'
        ]
    }
}

def diagnose_error(exit_code: int, logs: str) -> Dict:
    """Diagnose error from exit code and logs."""
    
    # Check for known patterns
    for error_type, config in ERROR_PATTERNS.items():
        for pattern in config['patterns']:
            if re.search(pattern, logs, re.IGNORECASE):
                return {
                    'error_type': error_type,
                    'message': f'{error_type.capitalize()} error detected',
                    'technical_details': logs[-500:],  # Last 500 chars
                    'suggestions': config['suggestions']
                }
    
    # Generic error based on exit code
    if exit_code == 10:
        return {
            'error_type': 'prerequisite',
            'message': 'Required tool not found',
            'technical_details': logs,
            'suggestions': ['Ensure Git is installed', 'Reinstall the application']
        }
    elif exit_code == 20:
        return {
            'error_type': 'configuration',
            'message': 'Configuration error',
            'technical_details': logs,
            'suggestions': ['Check your configuration settings', 'Go back and review each step']
        }
    else:
        return {
            'error_type': 'unknown',
            'message': 'An unexpected error occurred',
            'technical_details': logs,
            'suggestions': [
                'Try running the deployment again',
                'Check the technical details above',
                'Report this issue on GitHub if it persists'
            ]
        }

def main():
    """Main diagnosis entry point."""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: diagnose.py <exit_code> <logs>"}))
        sys.exit(1)
    
    exit_code = int(sys.argv[1])
    logs = sys.argv[2]
    
    diagnosis = diagnose_error(exit_code, logs)
    print(json.dumps(diagnosis))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test diagnosis**

Create `deployer/backend/test_diagnose.py`:

```python
#!/usr/bin/env python3
"""Tests for diagnosis script."""

import subprocess
import json

def test_network_error():
    """Test network error diagnosis."""
    logs = "Connection timeout: Could not reach github.com"
    result = subprocess.run(
        ['python3', 'diagnose.py', '1', logs],
        capture_output=True,
        text=True
    )
    diagnosis = json.loads(result.stdout)
    assert diagnosis['error_type'] == 'network'
    assert len(diagnosis['suggestions']) > 0
    print("✓ Network error diagnosed correctly")

def test_auth_error():
    """Test authentication error diagnosis."""
    logs = "401 Unauthorized: Bad credentials"
    result = subprocess.run(
        ['python3', 'diagnose.py', '1', logs],
        capture_output=True,
        text=True
    )
    diagnosis = json.loads(result.stdout)
    assert diagnosis['error_type'] == 'authentication'
    print("✓ Auth error diagnosed correctly")

if __name__ == '__main__':
    test_network_error()
    test_auth_error()
    print("✓ All diagnosis tests passed")
```

- [ ] **Step 3: Run tests**

```bash
cd deployer/backend
python3 test_diagnose.py
```

Expected: "✓ All diagnosis tests passed"

- [ ] **Step 4: Commit**

```bash
git add deployer/backend/diagnose.py deployer/backend/test_diagnose.py
git commit -m "feat(deployer): add error diagnosis with pattern matching"
```

---

## Task 11: Electron IPC Handlers

**Files:**
- Modify: `deployer/main.js`

- [ ] **Step 1: Add IPC handlers to main.js**

Add after the `app.on('activate')` block in `deployer/main.js`:

```javascript
// IPC Handlers

ipcMain.handle('validate-config', async (event, step, data) => {
  const python = process.platform === 'darwin' ? 'python3' : 'python';
  
  let validationType;
  let validationData;
  
  if (step === 1) {
    // Validate username, email, repo name
    const results = await Promise.all([
      runPythonScript([python, 'backend/validate.py', 'username', data.username]),
      runPythonScript([python, 'backend/validate.py', 'email', data.email]),
      runPythonScript([python, 'backend/validate.py', 'repo_name', data.repoName])
    ]);
    
    const allValid = results.every(r => r.valid);
    const errors = results.filter(r => !r.valid).map(r => r.error);
    
    return { valid: allValid, errors };
  }
  
  return { valid: true };
});

ipcMain.handle('test-github-token', async (event, token) => {
  const python = process.platform === 'darwin' ? 'python3' : 'python';
  const result = await runPythonScript([python, 'backend/validate.py', 'github_token', token]);
  return result;
});

ipcMain.handle('start-deploy', async (event, config) => {
  const python = process.platform === 'darwin' ? 'python3' : 'python';
  const configJson = JSON.stringify(config);
  
  return new Promise((resolve, reject) => {
    const deploy = spawn(python, ['backend/deploy.py', configJson], {
      cwd: __dirname
    });
    
    deploy.stdout.on('data', (data) => {
      const lines = data.toString().split('\n').filter(line => line.trim());
      lines.forEach(line => {
        try {
          const message = JSON.parse(line);
          
          if (message.type === 'progress') {
            mainWindow.webContents.send('deploy-progress', message);
          } else if (message.type === 'success') {
            mainWindow.webContents.send('deploy-success', message);
            resolve(message);
          } else if (message.type === 'error') {
            handleDeployError(message, data.toString()).then(diagnosis => {
              mainWindow.webContents.send('deploy-error', diagnosis);
              reject(diagnosis);
            });
          } else if (message.text) {
            mainWindow.webContents.send('deploy-log', message);
          }
        } catch (e) {
          // Not JSON, treat as log
          mainWindow.webContents.send('deploy-log', { text: line, level: 'info' });
        }
      });
    });
    
    deploy.stderr.on('data', (data) => {
      const text = data.toString();
      mainWindow.webContents.send('deploy-log', { text, level: 'error' });
    });
    
    deploy.on('close', (code) => {
      if (code !== 0 && code !== null) {
        handleDeployError({ exit_code: code }, '').then(diagnosis => {
          mainWindow.webContents.send('deploy-error', diagnosis);
          reject(diagnosis);
        });
      }
    });
  });
});

ipcMain.handle('retry-deploy', async (event) => {
  // Retry uses last config (stored in renderer state)
  return { status: 'ready_to_retry' };
});

ipcMain.handle('open-external', async (event, url) => {
  shell.openExternal(url);
  return { opened: true };
});

// Helper function to run Python scripts
function runPythonScript(args) {
  return new Promise((resolve, reject) => {
    const process = spawn(args[0], args.slice(1), {
      cwd: __dirname
    });
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    process.on('close', (code) => {
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        reject(new Error(`Failed to parse output: ${stdout} ${stderr}`));
      }
    });
  });
}

// Helper function to diagnose errors
async function handleDeployError(error, logs) {
  const python = process.platform === 'darwin' ? 'python3' : 'python';
  const exitCode = error.exit_code || 1;
  
  try {
    const diagnosis = await runPythonScript([
      python,
      'backend/diagnose.py',
      exitCode.toString(),
      logs || error.message || ''
    ]);
    return diagnosis;
  } catch (e) {
    return {
      error_type: 'unknown',
      message: error.message || 'Deployment failed',
      technical_details: logs || '',
      suggestions: ['Try again', 'Check your configuration']
    };
  }
}
```

- [ ] **Step 2: Test IPC communication**

Run: `npm run dev`
Try validating a username in Step 1
Expected: Validation calls Python script, returns result

- [ ] **Step 3: Commit**

```bash
git add deployer/main.js
git commit -m "feat(deployer): add IPC handlers for validation and deployment"
```

---

## Task 12: App Icon

**Files:**
- Create: `deployer/build/icon.icns`

- [ ] **Step 1: Create placeholder icon**

For development, create a simple icon or use a placeholder:

```bash
cd deployer/build
# Download a placeholder icon or create one
# For now, we'll skip this and use default Electron icon
touch icon.icns
```

- [ ] **Step 2: Note for later**

Log: "TODO: Replace with actual app icon before production build"

- [ ] **Step 3: Commit**

```bash
git add deployer/build/.gitkeep
git commit -m "chore(deployer): add build directory placeholder"
```

---

## Task 13: Build Script

**Files:**
- Create: `deployer/build_backend.py`

- [ ] **Step 1: Create build script for Python backend**

Create `deployer/build_backend.py`:

```python
#!/usr/bin/env python3
"""Build Python backend using PyInstaller."""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Build Python scripts into standalone executables."""
    print("Building Python backend...")
    
    backend_dir = Path(__file__).parent / 'backend'
    dist_dir = backend_dir / 'dist'
    build_dir = backend_dir / 'build'
    
    # Clean previous builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Check if PyInstaller is available
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Build each script
    scripts = ['deploy.py', 'validate.py', 'diagnose.py']
    
    for script in scripts:
        script_path = backend_dir / script
        print(f"Building {script}...")
        
        subprocess.run([
            'pyinstaller',
            '--onefile',
            '--name', script.replace('.py', ''),
            '--distpath', str(dist_dir),
            '--workpath', str(build_dir),
            '--specpath', str(build_dir),
            '--clean',
            str(script_path)
        ], check=True)
    
    print("✓ Python backend built successfully")
    print(f"Executables in: {dist_dir}")

if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Make build script executable**

```bash
chmod +x deployer/build_backend.py
```

- [ ] **Step 3: Test build (optional, takes time)**

```bash
cd deployer
python3 build_backend.py
```

Expected: Creates `backend/dist/` with executables

- [ ] **Step 4: Commit**

```bash
git add deployer/build_backend.py
git commit -m "feat(deployer): add Python backend build script using PyInstaller"
```

---

## Task 14: Final Integration Test

**Files:**
- None (testing only)

- [ ] **Step 1: Full development test**

```bash
cd deployer
npm run dev
```

Steps to test:
1. Fill Step 1 (username, email, repo)
2. Fill Step 2 (token) - use real token for full test
3. Review Step 3 (feeds)
4. Configure Step 4 (schedule)
5. Review Step 5
6. Click Deploy (test mode only, don't actually deploy)

Expected: All UI works, navigation smooth, validation triggers

- [ ] **Step 2: Check console for errors**

Open DevTools in Electron window
Expected: No JavaScript errors

- [ ] **Step 3: Document test results**

Create `deployer/TEST_RESULTS.md`:

```markdown
# Test Results

## Development Test - [Date]

### Passed
- ✓ App launches correctly
- ✓ All 5 steps load and render
- ✓ Navigation (Next/Back) works
- ✓ Form validation triggers
- ✓ Python scripts callable from main process
- ✓ IPC communication works

### Issues Found
- [ ] List any issues found

### Notes
- Full deployment test requires GitHub credentials
- Production build not yet tested
```

- [ ] **Step 4: Commit**

```bash
git add deployer/TEST_RESULTS.md
git commit -m "test(deployer): add integration test results"
```

---

## Task 15: Production Build

**Files:**
- Update: `deployer/package.json`

- [ ] **Step 1: Build Python backend**

```bash
cd deployer
npm run build:python
```

Expected: `backend/dist/` contains executables

- [ ] **Step 2: Build Electron app**

```bash
npm run build
```

Expected: `dist/AI Daily News Deployer.dmg` created

- [ ] **Step 3: Test DMG installation**

1. Open the DMG file
2. Drag app to Applications
3. Launch from Applications
4. Test basic functionality

Expected: App works as standalone application

- [ ] **Step 4: Document build**

Add to `deployer/README.md`:

```markdown
## Build

### Full Build
```bash
npm run build:all
```

Output: `dist/AI Daily News Deployer.dmg` (~150MB)

### Installation
1. Open the DMG file
2. Drag "AI Daily News Deployer" to Applications
3. Launch from Applications or Spotlight

### First Run
macOS may show "unidentified developer" warning:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog
```

- [ ] **Step 5: Commit**

```bash
git add deployer/README.md
git commit -m "docs(deployer): add production build instructions"
```

---

## Task 16: Final Documentation

**Files:**
- Create: `deployer/DEPLOYMENT_GUIDE.md`
- Update: `/Users/lixiaochen/Desktop/ai-daily-news/README.md`

- [ ] **Step 1: Create deployment guide**

Create `deployer/DEPLOYMENT_GUIDE.md`:

```markdown
# AI Daily News Deployer - User Guide

## Prerequisites
- macOS 10.15 or later
- GitHub account
- Internet connection

## Installation

1. Download `AI Daily News Deployer.dmg`
2. Open the DMG file
3. Drag the app to your Applications folder
4. Launch from Applications or Spotlight

## First Run

If you see "unidentified developer" warning:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the security dialog

## Usage

### Step 1: Basic Information
- Enter your GitHub username
- Enter your email address
- Choose a repository name (default: ai-daily-news)

### Step 2: GitHub Authentication
1. Click "Get Token from GitHub"
2. Create a new token with these permissions:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Actions workflows)
3. Copy the token
4. Paste it into the app

### Step 3: RSS Feeds
- Review the 15 pre-configured AI+Design feeds
- Add custom feeds if desired
- Remove any feeds you don't want

### Step 4: Advanced Options
- Set update frequency (default: daily at 10 AM Beijing time)
- Choose timezone
- Optional: Enable AgentMail integration

### Step 5: Deploy
1. Review your configuration
2. Click "Deploy"
3. Wait for deployment to complete (2-3 minutes)
4. Click the links to view your site

## After Deployment

Your AI Daily News site will update automatically based on your schedule.

### View Your Site
https://[your-username].github.io/[repo-name]/

### Manage Settings
1. Go to your repository on GitHub
2. Click "Settings"
3. Configure GitHub Pages, Actions, or Secrets

### Update Feeds
1. Edit `feeds/follow.opml` in your repository
2. Commit and push changes
3. Next update will use new feeds

## Troubleshooting

### "Invalid token" error
- Ensure token has `repo` and `workflow` permissions
- Check token hasn't expired
- Generate a new token if needed

### "Repository already exists" error
- The deployer will update your existing repository
- Or choose a different repository name

### Deployment fails
- Check internet connection
- Verify GitHub credentials
- Review error details in the app
- Try again after fixing suggested issues

## Support

Report issues: https://github.com/[your-repo]/issues
```

- [ ] **Step 2: Update main README**

Add to `/Users/lixiaochen/Desktop/ai-daily-news/README.md` after the "快速开始" section:

```markdown
## 🚀 一键部署工具（推荐）

我们提供了一个图形化部署工具，无需终端命令，点击几下即可完成部署。

1. 下载 [AI Daily News Deployer.dmg](releases)
2. 双击打开，拖入应用程序文件夹
3. 启动应用，按照向导完成配置
4. 3分钟内完成部署到 GitHub Pages

详细使用说明：[deployer/DEPLOYMENT_GUIDE.md](deployer/DEPLOYMENT_GUIDE.md)
```

- [ ] **Step 3: Commit**

```bash
git add deployer/DEPLOYMENT_GUIDE.md
git add README.md
git commit -m "docs: add deployment guide and update main README"
```

---

## Final Checklist

- [ ] All 16 tasks completed
- [ ] All tests passing
- [ ] Production build successful
- [ ] Documentation complete
- [ ] Code committed to git

---

## Success Criteria

✓ Double-click .app launches Electron window
✓ 5-step wizard navigable with validation
✓ Python scripts callable from Electron
✓ Can input all configuration fields
✓ Deployment executes and shows progress
✓ Errors diagnosed with suggestions
✓ Success state shows GitHub links
✓ DMG file builds successfully (~150MB)
✓ Standalone app works without dependencies

---

**Estimated Time:** 24 hours (3 days)
**Complexity:** Medium-High
**Dependencies:** Electron, Node.js, Python, macOS development environment
