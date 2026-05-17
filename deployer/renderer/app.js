/**
 * AI Daily News Deployer - Frontend Application
 * Complete wizard state management and UI logic
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

const state = {
  currentStep: 1,
  maxStep: 5,
  config: {
    // Step 1: Basic Info
    githubUsername: '',
    email: '',
    repoName: '',
    glmApiKey: '',
    easyrouterApiKey: '',

    // Step 2: GitHub Auth
    githubToken: '',
    saveToken: false,
    tokenVerified: false,

    // Step 3: RSS Feeds
    feeds: [],

    // Step 4: Advanced Options
    updateSchedule: '0 0 * * *',
    customCron: '',
    timezone: 'UTC',
    articlesPerPage: 20,
    enableComments: false,
    enableAnalytics: false
  }
};

// ============================================================================
// DOM ELEMENT REFERENCES
// ============================================================================

const elements = {
  stepContent: null,
  btnBack: null,
  btnNext: null,
  stepIndicators: null
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  console.log('App initializing...');

  // Get DOM references
  elements.stepContent = document.getElementById('step-content');
  elements.btnBack = document.getElementById('btn-back');
  elements.btnNext = document.getElementById('btn-next');
  elements.stepIndicators = document.querySelectorAll('.steps .step');

  // Set up navigation handlers
  elements.btnBack.addEventListener('click', handleBack);
  elements.btnNext.addEventListener('click', handleNext);

  // Render initial step
  renderStep(state.currentStep);
  updateNavigation();

  console.log('App initialized');
});

// ============================================================================
// NAVIGATION HANDLERS
// ============================================================================

function handleBack() {
  if (state.currentStep > 1) {
    state.currentStep--;
    renderStep(state.currentStep);
    updateNavigation();
  }
}

function handleNext() {
  // Validate current step before proceeding
  if (validateCurrentStep()) {
    if (state.currentStep < state.maxStep) {
      state.currentStep++;
      renderStep(state.currentStep);
      updateNavigation();
    }
  }
}

function updateNavigation() {
  // Update back button
  elements.btnBack.disabled = state.currentStep === 1;

  // Update next button
  if (state.currentStep === state.maxStep) {
    elements.btnNext.style.display = 'none';
  } else {
    elements.btnNext.style.display = 'flex';
    elements.btnNext.textContent = 'Next';
  }

  // Update step indicators
  elements.stepIndicators.forEach((indicator, index) => {
    const stepNum = index + 1;
    if (stepNum < state.currentStep) {
      indicator.classList.add('step-primary');
    } else if (stepNum === state.currentStep) {
      indicator.classList.add('step-primary');
    } else {
      indicator.classList.remove('step-primary');
    }
  });
}

// ============================================================================
// STEP RENDERING
// ============================================================================

function renderStep(stepNum) {
  console.log(`Rendering step ${stepNum}`);

  // Get template
  const template = document.getElementById(`step${stepNum}-template`);
  if (!template) {
    console.error(`Template for step ${stepNum} not found`);
    return;
  }

  // Clone template content
  const content = template.content.cloneNode(true);

  // Clear and insert content
  elements.stepContent.innerHTML = '';
  elements.stepContent.appendChild(content);

  // Set up step-specific handlers
  switch (stepNum) {
    case 1:
      setupStep1Handlers();
      break;
    case 2:
      setupStep2Handlers();
      break;
    case 3:
      setupStep3Handlers();
      break;
    case 4:
      setupStep4Handlers();
      break;
    case 5:
      setupStep5Handlers();
      break;
  }
}

// ============================================================================
// STEP 1: BASIC INFO
// ============================================================================

function setupStep1Handlers() {
  const usernameInput = document.getElementById('github-username');
  const emailInput = document.getElementById('email');
  const repoInput = document.getElementById('repo-name');
  const glmKeyInput = document.getElementById('glm-api-key');
  const toggleGlmBtn = document.getElementById('toggle-glm-key');
  const glmEyeIcon = document.getElementById('eye-icon-glm');
  const apiKeyInput = document.getElementById('easyrouter-api-key');
  const toggleApiKeyBtn = document.getElementById('toggle-api-key-step1');
  const eyeIcon = document.getElementById('eye-icon-step1');

  // Restore saved values
  if (state.config.githubUsername) usernameInput.value = state.config.githubUsername;
  if (state.config.email) emailInput.value = state.config.email;
  if (state.config.repoName) repoInput.value = state.config.repoName;
  if (state.config.glmApiKey) glmKeyInput.value = state.config.glmApiKey;
  if (state.config.easyrouterApiKey) apiKeyInput.value = state.config.easyrouterApiKey;

  // Update preview in real-time
  usernameInput.addEventListener('input', (e) => {
    state.config.githubUsername = e.target.value.trim();
    updateSitePreview();
  });

  emailInput.addEventListener('input', (e) => {
    state.config.email = e.target.value.trim();
  });

  repoInput.addEventListener('input', (e) => {
    state.config.repoName = e.target.value.trim();
    updateSitePreview();
  });

  glmKeyInput.addEventListener('input', (e) => {
    state.config.glmApiKey = e.target.value.trim();
  });

  apiKeyInput.addEventListener('input', (e) => {
    state.config.easyrouterApiKey = e.target.value.trim();
  });

  // Toggle GLM key visibility
  toggleGlmBtn.addEventListener('click', () => {
    if (glmKeyInput.type === 'password') {
      glmKeyInput.type = 'text';
      glmEyeIcon.textContent = '🙈';
    } else {
      glmKeyInput.type = 'password';
      glmEyeIcon.textContent = '👁️';
    }
  });

  // Toggle EasyRouter key visibility
  toggleApiKeyBtn.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
      eyeIcon.textContent = '🙈';
    } else {
      apiKeyInput.type = 'password';
      eyeIcon.textContent = '👁️';
    }
  });

  // Initial preview update
  updateSitePreview();
}

function updateSitePreview() {
  const usernamePreview = document.querySelector('.username-preview');
  const repoPreview = document.querySelector('.repo-preview');

  if (usernamePreview) {
    usernamePreview.textContent = state.config.githubUsername || 'username';
  }

  if (repoPreview) {
    repoPreview.textContent = state.config.repoName || 'repo-name';
  }
}

function validateStep1() {
  const username = state.config.githubUsername;
  const email = state.config.email;
  const repoName = state.config.repoName;

  // Validate username
  if (!username || username.length === 0) {
    showError('Please enter your GitHub username');
    return false;
  }

  // Validate email
  if (!email || email.length === 0) {
    showError('Please enter your email address');
    return false;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showError('Please enter a valid email address');
    return false;
  }

  // Validate repo name
  if (!repoName || repoName.length === 0) {
    showError('Please enter a repository name');
    return false;
  }

  const repoRegex = /^[a-zA-Z0-9-_]+$/;
  if (!repoRegex.test(repoName)) {
    showError('Repository name can only contain letters, numbers, hyphens, and underscores');
    return false;
  }

  return true;
}

// ============================================================================
// STEP 2: GITHUB AUTHENTICATION
// ============================================================================

function setupStep2Handlers() {
  const tokenInput = document.getElementById('github-token');
  const saveTokenCheckbox = document.getElementById('save-token');
  const verifyButton = document.getElementById('verify-token');
  const githubTokenLink = document.getElementById('github-token-link');

  // Restore saved values
  if (state.config.githubToken) tokenInput.value = state.config.githubToken;
  if (state.config.saveToken) saveTokenCheckbox.checked = state.config.saveToken;

  // Save values to state
  tokenInput.addEventListener('input', (e) => {
    state.config.githubToken = e.target.value.trim();
    state.config.tokenVerified = false;
  });

  saveTokenCheckbox.addEventListener('change', (e) => {
    state.config.saveToken = e.target.checked;
  });

  // Verify token button
  verifyButton.addEventListener('click', () => {
    verifyGitHubToken();
  });

  // Open GitHub token page
  githubTokenLink.addEventListener('click', (e) => {
    e.preventDefault();
    openExternalLink('https://github.com/settings/tokens/new');
  });
}

async function verifyGitHubToken() {
  const token = state.config.githubToken;

  if (!token || token.length === 0) {
    showTokenStatus('error', '请输入令牌');
    return;
  }

  const statusDiv = document.getElementById('token-status');
  statusDiv.classList.remove('hidden');
  statusDiv.innerHTML = `
    <div class="alert alert-info">
      <span class="loading loading-spinner loading-sm"></span>
      <span>正在验证令牌...</span>
    </div>
  `;

  try {
    // Use Electron API if available
    if (window.electronAPI && window.electronAPI.verifyGitHubToken) {
      const result = await window.electronAPI.verifyGitHubToken(token);

      if (result.success) {
        state.config.tokenVerified = result.hasRequiredScopes;

        if (result.hasRequiredScopes) {
          showTokenStatus('success', `令牌验证成功！用户：${result.username}`);
        } else {
          showTokenStatus('warning', `令牌有效但缺少必要权限。需要：repo 和 workflow。当前权限：${result.scopes.join(', ')}`);
        }
      } else {
        state.config.tokenVerified = false;
        showTokenStatus('error', `验证失败：${result.error}`);
      }
    } else {
      // Fallback: basic format validation
      if (token.startsWith('ghp_') || token.startsWith('github_pat_')) {
        state.config.tokenVerified = true;
        showTokenStatus('success', '令牌格式有效（未进行完整验证）');
      } else {
        state.config.tokenVerified = false;
        showTokenStatus('warning', '令牌格式看起来不正确。请确保包含 repo 和 workflow 权限。');
      }
    }
  } catch (error) {
    state.config.tokenVerified = false;
    showTokenStatus('error', `验证失败：${error.message}`);
  }
}

function showTokenStatus(type, message) {
  const statusDiv = document.getElementById('token-status');
  statusDiv.classList.remove('hidden');

  const alertClass = type === 'success' ? 'alert-success' :
                     type === 'error' ? 'alert-error' :
                     type === 'warning' ? 'alert-warning' : 'alert-info';

  const icon = type === 'success' ?
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />' :
    type === 'error' ?
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />' :
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />';

  statusDiv.innerHTML = `
    <div class="alert ${alertClass}">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        ${icon}
      </svg>
      <span>${message}</span>
    </div>
  `;
}

function validateStep2() {
  const token = state.config.githubToken;

  if (!token || token.length === 0) {
    showError('Please enter your GitHub Personal Access Token');
    return false;
  }

  // Basic format check
  if (!token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
    showError('Token format looks invalid. GitHub tokens should start with "ghp_" or "github_pat_"');
    return false;
  }

  if (token.length < 20) {
    showError('Token appears to be too short. Please check your token.');
    return false;
  }

  return true;
}

// ============================================================================
// STEP 3: RSS FEEDS
// ============================================================================

function setupStep3Handlers() {
  const feedUrlInput = document.getElementById('feed-url');
  const addFeedButton = document.getElementById('add-feed');
  const suggestedFeedButtons = document.querySelectorAll('.suggested-feed');

  // Add feed button
  addFeedButton.addEventListener('click', () => {
    const url = feedUrlInput.value.trim();
    if (url) {
      addFeed(url);
      feedUrlInput.value = '';
    }
  });

  // Enter key to add feed
  feedUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const url = feedUrlInput.value.trim();
      if (url) {
        addFeed(url);
        feedUrlInput.value = '';
      }
    }
  });

  // Suggested feeds
  suggestedFeedButtons.forEach(button => {
    button.addEventListener('click', () => {
      const url = button.getAttribute('data-url');
      addFeed(url);
    });
  });

  // Add all design feeds button
  const addAllDesignButton = document.getElementById('add-all-design-feeds');
  if (addAllDesignButton) {
    addAllDesignButton.addEventListener('click', () => {
      const designFeeds = [
        'https://rsshub.pseudoyu.com/twitter/user/ryolu',
        'https://rsshub.pseudoyu.com/twitter/user/Gavmn',
        'https://rsshub.pseudoyu.com/twitter/user/op7418',
        'https://rsshub.pseudoyu.com/twitter/user/raunofreiberg',
        'https://rsshub.pseudoyu.com/twitter/user/Jakubantalik',
        'https://rsshub.pseudoyu.com/twitter/user/zielinskiwoj',
        'https://rsshub.pseudoyu.com/twitter/user/mattsilx',
        'https://rsshub.pseudoyu.com/twitter/user/eduardbodak',
        'https://rsshub.pseudoyu.com/twitter/user/reactivve_',
        'https://rsshub.pseudoyu.com/twitter/user/designgurra',
        'https://rsshub.pseudoyu.com/twitter/user/berryxia'
      ];

      let addedCount = 0;
      designFeeds.forEach(url => {
        if (!state.config.feeds.includes(url)) {
          state.config.feeds.push(url);
          addedCount++;
        }
      });

      renderFeedsList();

      if (addedCount > 0) {
        showSuccess(`成功添加 ${addedCount} 个设计博主订阅源！`);
      } else {
        showSuccess('所有设计博主已在列表中');
      }
    });
  }

  // Render existing feeds
  renderFeedsList();
}

function addFeed(url) {
  // Validate URL
  try {
    new URL(url);
  } catch (e) {
    showError('Please enter a valid URL');
    return;
  }

  // Check for duplicates
  if (state.config.feeds.includes(url)) {
    showError('This feed has already been added');
    return;
  }

  // Add to state
  state.config.feeds.push(url);

  // Re-render list
  renderFeedsList();

  console.log('Feed added:', url);
}

function removeFeed(url) {
  const index = state.config.feeds.indexOf(url);
  if (index > -1) {
    state.config.feeds.splice(index, 1);
    renderFeedsList();
    console.log('Feed removed:', url);
  }
}

function renderFeedsList() {
  const feedsList = document.getElementById('feeds-list');

  if (state.config.feeds.length === 0) {
    feedsList.innerHTML = `
      <div class="alert alert-info">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>No feeds added yet. Add at least one RSS feed to continue.</span>
      </div>
    `;
    return;
  }

  feedsList.innerHTML = state.config.feeds.map((url, index) => `
    <div class="alert shadow-sm">
      <div class="flex-1 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7m-6 0a1 1 0 11-2 0 1 1 0 012 0z" />
        </svg>
        <span class="text-sm font-mono truncate">${url}</span>
      </div>
      <button class="btn btn-ghost btn-sm btn-square" onclick="removeFeed('${url}')">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  `).join('');
}

// Make removeFeed globally accessible for onclick handlers
window.removeFeed = removeFeed;

function validateStep3() {
  if (state.config.feeds.length === 0) {
    showError('请至少添加一个 RSS 订阅源');
    return false;
  }

  return true;
}

// ============================================================================
// STEP 4: ADVANCED OPTIONS
// ============================================================================

function setupStep4Handlers() {
  const scheduleSelect = document.getElementById('update-schedule');
  const customCronContainer = document.getElementById('custom-cron-container');
  const customCronInput = document.getElementById('custom-cron');
  const timezoneSelect = document.getElementById('timezone');
  const articlesInput = document.getElementById('articles-per-page');
  const commentsCheckbox = document.getElementById('enable-comments');
  const analyticsCheckbox = document.getElementById('enable-analytics');
  const cronHelpLink = document.getElementById('cron-help-link');

  // Restore saved values
  if (state.config.updateSchedule) scheduleSelect.value = state.config.updateSchedule;
  if (state.config.customCron) customCronInput.value = state.config.customCron;
  if (state.config.timezone) timezoneSelect.value = state.config.timezone;
  if (state.config.articlesPerPage) articlesInput.value = state.config.articlesPerPage;
  commentsCheckbox.checked = state.config.enableComments;
  analyticsCheckbox.checked = state.config.enableAnalytics;

  // Show/hide custom cron input
  scheduleSelect.addEventListener('change', (e) => {
    const value = e.target.value;
    if (value === 'custom') {
      customCronContainer.classList.remove('hidden');
      state.config.updateSchedule = state.config.customCron || '0 */6 * * *';
    } else {
      customCronContainer.classList.add('hidden');
      state.config.updateSchedule = value;
    }
  });

  // Custom cron input
  customCronInput.addEventListener('input', (e) => {
    state.config.customCron = e.target.value.trim();
    if (scheduleSelect.value === 'custom') {
      state.config.updateSchedule = state.config.customCron;
    }
  });

  // Timezone
  timezoneSelect.addEventListener('change', (e) => {
    state.config.timezone = e.target.value;
  });

  // Articles per page
  articlesInput.addEventListener('input', (e) => {
    const value = parseInt(e.target.value, 10);
    if (value >= 5 && value <= 100) {
      state.config.articlesPerPage = value;
    }
  });

  // Checkboxes
  commentsCheckbox.addEventListener('change', (e) => {
    state.config.enableComments = e.target.checked;
  });

  analyticsCheckbox.addEventListener('change', (e) => {
    state.config.enableAnalytics = e.target.checked;
  });

  // Cron help link
  cronHelpLink.addEventListener('click', (e) => {
    e.preventDefault();
    openExternalLink('https://crontab.guru/');
  });

  // Initial custom cron visibility
  if (scheduleSelect.value === 'custom') {
    customCronContainer.classList.remove('hidden');
  }
}

function validateStep4() {
  const articlesPerPage = state.config.articlesPerPage;

  // Validate articles per page
  if (articlesPerPage < 5 || articlesPerPage > 100) {
    showError('Articles per page must be between 5 and 100');
    return false;
  }

  // Validate custom cron if selected
  const scheduleSelect = document.getElementById('update-schedule');
  if (scheduleSelect && scheduleSelect.value === 'custom') {
    const cron = state.config.customCron;
    if (!cron || cron.trim().length === 0) {
      showError('Please enter a custom cron expression');
      return false;
    }

    // Basic cron validation (5 parts)
    const cronParts = cron.trim().split(/\s+/);
    if (cronParts.length !== 5) {
      showError('Cron expression must have 5 parts (minute hour day month weekday)');
      return false;
    }
  }

  return true;
}

// ============================================================================
// STEP 5: REVIEW & DEPLOY
// ============================================================================

function setupStep5Handlers() {
  // Populate configuration summary
  populateConfigSummary();

  // Deploy button
  const deployButton = document.getElementById('btn-deploy');
  if (deployButton) {
    deployButton.addEventListener('click', handleDeploy);
  }

  // Retry button (in error state)
  const retryButton = document.getElementById('btn-retry');
  if (retryButton) {
    retryButton.addEventListener('click', handleDeploy);
  }

  // Back to config button (in error state)
  const backToConfigButton = document.getElementById('btn-back-to-config');
  if (backToConfigButton) {
    backToConfigButton.addEventListener('click', () => {
      // Hide error state, show deploy actions
      document.getElementById('deploy-error').classList.add('hidden');
      document.getElementById('deploy-actions').classList.remove('hidden');
    });
  }

  // New deployment button (in success state)
  const newDeployButton = document.getElementById('btn-new-deployment');
  if (newDeployButton) {
    newDeployButton.addEventListener('click', () => {
      // Reset state and go back to step 1
      resetState();
      state.currentStep = 1;
      renderStep(1);
      updateNavigation();
    });
  }

  // Copy URL buttons (in success state)
  const copyUrlButton = document.getElementById('copy-url');
  if (copyUrlButton) {
    copyUrlButton.addEventListener('click', () => {
      const urlInput = document.getElementById('site-url');
      urlInput.select();
      document.execCommand('copy');
      showSuccess('URL copied to clipboard!');
    });
  }

  const copyRepoUrlButton = document.getElementById('copy-repo-url');
  if (copyRepoUrlButton) {
    copyRepoUrlButton.addEventListener('click', () => {
      const urlInput = document.getElementById('repo-url');
      urlInput.select();
      document.execCommand('copy');
      showSuccess('Repository URL copied to clipboard!');
    });
  }

  // Open site/repo buttons (in success state)
  const openSiteButton = document.getElementById('open-site');
  if (openSiteButton) {
    openSiteButton.addEventListener('click', () => {
      const url = `https://${state.config.githubUsername}.github.io/${state.config.repoName}`;
      openExternalLink(url);
    });
  }

  const openRepoButton = document.getElementById('open-repo');
  if (openRepoButton) {
    openRepoButton.addEventListener('click', () => {
      const url = `https://github.com/${state.config.githubUsername}/${state.config.repoName}`;
      openExternalLink(url);
    });
  }
}

function populateConfigSummary() {
  // Basic information
  document.getElementById('summary-username').textContent = state.config.githubUsername || '-';
  document.getElementById('summary-email').textContent = state.config.email || '-';
  document.getElementById('summary-repo').textContent = state.config.repoName || '-';

  // AI Filter status
  const aiFilterStatus = document.getElementById('summary-ai-filter');
  const hasGlm = state.config.glmApiKey;
  const hasEasyRouter = state.config.easyrouterApiKey;

  if (hasGlm && hasEasyRouter) {
    aiFilterStatus.innerHTML = '<span class="badge badge-success badge-sm">完整配置（免费初筛+深度分析）</span>';
  } else if (hasEasyRouter) {
    aiFilterStatus.innerHTML = '<span class="badge badge-warning badge-sm">仅深度分析（跳过GLM初筛）</span>';
  } else if (hasGlm) {
    aiFilterStatus.innerHTML = '<span class="badge badge-warning badge-sm">仅GLM初筛（无深度分析）</span>';
  } else {
    aiFilterStatus.innerHTML = '<span class="badge badge-ghost badge-sm">未配置（仅关键词筛选）</span>';
  }

  // RSS Feeds
  const summaryFeeds = document.getElementById('summary-feeds');
  if (state.config.feeds.length === 0) {
    summaryFeeds.innerHTML = '<div class="text-base-content/70">未添加订阅源</div>';
  } else {
    summaryFeeds.innerHTML = state.config.feeds.map(feed =>
      `<div class="flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7m-6 0a1 1 0 11-2 0 1 1 0 012 0z" />
        </svg>
        <span class="font-mono text-xs truncate">${feed}</span>
      </div>`
    ).join('');
  }

  // Advanced settings
  document.getElementById('summary-schedule').textContent = getScheduleDescription(state.config.updateSchedule);
  document.getElementById('summary-timezone').textContent = state.config.timezone || 'UTC';
  document.getElementById('summary-articles').textContent = state.config.articlesPerPage || '20';
  document.getElementById('summary-comments').textContent = state.config.enableComments ? '已启用' : '已禁用';
  document.getElementById('summary-analytics').textContent = state.config.enableAnalytics ? '已启用' : '已禁用';
}

function getScheduleDescription(cron) {
  const scheduleMap = {
    '0 */6 * * *': '每 6 小时',
    '0 */12 * * *': '每 12 小时',
    '0 0 * * *': '每天午夜',
    '0 0 * * 1': '每周一次（周一）'
  };

  return scheduleMap[cron] || `自定义: ${cron}`;
}

async function handleDeploy() {
  console.log('Starting deployment with config:', state.config);

  // Hide deploy actions, show progress
  const deployActions = document.getElementById('deploy-actions');
  const deployProgress = document.getElementById('deploy-progress');
  const deploySuccess = document.getElementById('deploy-success');
  const deployError = document.getElementById('deploy-error');

  deployActions.classList.add('hidden');
  deployProgress.classList.remove('hidden');
  deploySuccess.classList.add('hidden');
  deployError.classList.add('hidden');

  // Reset progress steps
  const progressSteps = [
    'progress-repo',
    'progress-files',
    'progress-actions',
    'progress-pages',
    'progress-complete'
  ];

  progressSteps.forEach(stepId => {
    const step = document.getElementById(stepId);
    if (step) {
      step.classList.remove('step-primary', 'step-error');
      step.setAttribute('data-status', 'pending');
    }
  });

  // Clear progress log
  const progressLog = document.getElementById('progress-log');
  progressLog.innerHTML = '<pre data-prefix="$"><code>正在开始部署...</code></pre>';

  // Set up progress listeners
  if (window.electronAPI) {
    // Listen for progress updates
    window.electronAPI.onDeployProgress((data) => {
      handleDeployProgress(data);
    });

    // Listen for completion
    window.electronAPI.onDeployComplete((data) => {
      handleDeployComplete(data);
    });

    // Listen for errors
    window.electronAPI.onDeployError((data) => {
      handleDeployError(data);
    });

    try {
      // Start real deployment
      const deployConfig = getDeploymentConfig();
      await window.electronAPI.startDeploy(deployConfig);
    } catch (error) {
      console.error('Failed to start deployment:', error);
      handleDeployError({
        error: error.message,
        details: error.stack
      });
    }
  } else {
    // Fallback: simulate deployment for testing without Electron
    try {
      await simulateDeploymentStep('progress-repo', '正在创建仓库...', 1500);
      await simulateDeploymentStep('progress-files', '正在上传文件...', 2000);
      await simulateDeploymentStep('progress-actions', '正在配置 GitHub Actions...', 1500);
      await simulateDeploymentStep('progress-pages', '正在启用 GitHub Pages...', 1500);
      await simulateDeploymentStep('progress-complete', '正在完成部署...', 1000);

      // Show success state
      deployProgress.classList.add('hidden');
      deploySuccess.classList.remove('hidden');

      // Update URLs
      const siteUrl = `https://${state.config.githubUsername}.github.io/${state.config.repoName}`;
      const repoUrl = `https://github.com/${state.config.githubUsername}/${state.config.repoName}`;

      document.getElementById('site-url').value = siteUrl;
      document.getElementById('repo-url').value = repoUrl;

      addProgressLog('部署完成！', 'success');

    } catch (error) {
      console.error('Deployment failed:', error);
      handleDeployError({
        error: error.message,
        details: error.stack
      });
    }
  }
}

function handleDeployProgress(data) {
  const { stepId, message, status } = data;

  // Update step indicator
  const step = document.getElementById(stepId);
  if (step) {
    if (status === 'in-progress') {
      step.classList.add('step-primary');
    } else if (status === 'complete') {
      step.classList.add('step-primary');
    }
    step.setAttribute('data-status', status);
  }

  // Add to progress log
  const progressType = status === 'complete' ? 'success' : status === 'info' ? 'info' : 'info';
  addProgressLog(message, progressType);
}

function handleDeployComplete(data) {
  const { siteUrl, repoUrl } = data;

  // Hide progress, show success
  document.getElementById('deploy-progress').classList.add('hidden');
  document.getElementById('deploy-success').classList.remove('hidden');

  // Update URLs
  document.getElementById('site-url').value = siteUrl;
  document.getElementById('repo-url').value = repoUrl;

  addProgressLog('🎉 部署成功完成！', 'success');
}

function handleDeployError(data) {
  const { error, details } = data;

  // Hide progress, show error
  document.getElementById('deploy-progress').classList.add('hidden');
  document.getElementById('deploy-error').classList.remove('hidden');

  document.getElementById('error-message').textContent = error || '部署过程中发生错误';
  document.getElementById('error-details').textContent = details || error;

  addProgressLog(`❌ 错误: ${error}`, 'error');
}

async function simulateDeploymentStep(stepId, message, duration) {
  const step = document.getElementById(stepId);
  if (step) {
    step.classList.add('step-primary');
    step.setAttribute('data-status', 'in-progress');
  }

  addProgressLog(message);

  await new Promise(resolve => setTimeout(resolve, duration));

  if (step) {
    step.setAttribute('data-status', 'complete');
  }

  // 特殊处理 GitHub Pages 步骤
  if (stepId === 'progress-pages') {
    addProgressLog(`${message} ✓`, 'success');
    addProgressLog('提示：GitHub Pages 首次构建需要 1-2 分钟，请稍候再访问网站', 'info');
  } else {
    addProgressLog(`${message} ✓`, 'success');
  }
}

function addProgressLog(message, type = 'info') {
  const progressLog = document.getElementById('progress-log');
  const prefix = type === 'error' ? '✗' : type === 'success' ? '✓' : '$';
  const line = document.createElement('pre');
  line.setAttribute('data-prefix', prefix);

  const code = document.createElement('code');
  code.textContent = message;
  line.appendChild(code);

  if (type === 'error') {
    code.classList.add('text-error');
  } else if (type === 'success') {
    code.classList.add('text-success');
  }

  progressLog.appendChild(line);

  // Auto-scroll to bottom
  progressLog.scrollTop = progressLog.scrollHeight;
}

function validateStep5() {
  // No validation needed for review step
  return true;
}

// ============================================================================
// VALIDATION
// ============================================================================

function validateCurrentStep() {
  switch (state.currentStep) {
    case 1:
      return validateStep1();
    case 2:
      return validateStep2();
    case 3:
      return validateStep3();
    case 4:
      return validateStep4();
    case 5:
      return validateStep5();
    default:
      return true;
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showError(message) {
  // Create toast notification
  const toast = document.createElement('div');
  toast.className = 'toast toast-top toast-center z-50';
  toast.innerHTML = `
    <div class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>${message}</span>
    </div>
  `;

  document.body.appendChild(toast);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

function showSuccess(message) {
  // Create toast notification
  const toast = document.createElement('div');
  toast.className = 'toast toast-top toast-center z-50';
  toast.innerHTML = `
    <div class="alert alert-success">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>${message}</span>
    </div>
  `;

  document.body.appendChild(toast);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

function openExternalLink(url) {
  // Use Electron API if available, otherwise fallback to window.open
  if (window.electronAPI && window.electronAPI.openExternal) {
    window.electronAPI.openExternal(url);
  } else {
    window.open(url, '_blank');
  }
}

function resetState() {
  state.currentStep = 1;
  state.config = {
    githubUsername: '',
    email: '',
    repoName: '',
    githubToken: '',
    saveToken: false,
    tokenVerified: false,
    feeds: [],
    updateSchedule: '0 0 * * *',
    customCron: '',
    timezone: 'UTC',
    articlesPerPage: 20,
    enableComments: false,
    enableAnalytics: false
  };
}

// ============================================================================
// EXPORT STATE FOR BACKEND
// ============================================================================

function getDeploymentConfig() {
  return {
    github: {
      username: state.config.githubUsername,
      email: state.config.email,
      repoName: state.config.repoName,
      token: state.config.githubToken,
      saveToken: state.config.saveToken
    },
    feeds: state.config.feeds,
    settings: {
      updateSchedule: state.config.updateSchedule,
      timezone: state.config.timezone,
      articlesPerPage: state.config.articlesPerPage,
      enableComments: state.config.enableComments,
      enableAnalytics: state.config.enableAnalytics
    },
    secrets: {
      glmApiKey: state.config.glmApiKey,
      easyrouterApiKey: state.config.easyrouterApiKey
    }
  };
}

// Make getDeploymentConfig globally accessible
window.getDeploymentConfig = getDeploymentConfig;

console.log('App.js loaded successfully');
