const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs').promises;

let mainWindow;
let deploymentConfig = null;
let Octokit = null;

// Dynamically import Octokit (ES Module)
async function loadOctokit() {
  if (!Octokit) {
    const octokitModule = await import('@octokit/rest');
    Octokit = octokitModule.Octokit;
  }
  return Octokit;
}

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

app.whenReady().then(() => {
  console.log('Preload script path:', path.join(__dirname, 'preload.js'));
  setupIpcHandlers();
  createWindow();
});

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

// ============================================================================
// IPC Handlers
// ============================================================================

function setupIpcHandlers() {
  // Open external URL
  ipcMain.handle('open-external', async (event, url) => {
    await shell.openExternal(url);
  });

  // Get app version
  ipcMain.handle('get-version', () => {
    return app.getVersion();
  });

  // Verify GitHub token
  ipcMain.handle('verify-github-token', async (event, token) => {
    try {
      await loadOctokit();
      const octokit = new Octokit({ auth: token });
      const { data: user } = await octokit.rest.users.getAuthenticated();

      // Check token scopes
      const { headers } = await octokit.request('HEAD /');
      const scopes = headers['x-oauth-scopes']?.split(',').map(s => s.trim()) || [];

      return {
        success: true,
        username: user.login,
        scopes: scopes,
        hasRequiredScopes: scopes.includes('repo') && scopes.includes('workflow')
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  });

  // Start deployment
  ipcMain.handle('start-deploy', async (event, config) => {
    deploymentConfig = config;

    try {
      // Initialize Octokit
      await loadOctokit();
      const octokit = new Octokit({ auth: config.github.token });

      // Step 1: Create repository
      sendProgress('progress-repo', '正在创建仓库...', 'in-progress');
      const repo = await createRepository(octokit, config);
      sendProgress('progress-repo', '仓库创建成功 ✓', 'complete');

      // Step 2: Upload files
      sendProgress('progress-files', '正在上传文件...', 'in-progress');
      await uploadProjectFiles(octokit, config, repo);
      sendProgress('progress-files', '文件上传成功 ✓', 'complete');

      // Step 3: Configure GitHub Actions
      sendProgress('progress-actions', '正在配置 GitHub Actions...', 'in-progress');
      await configureGitHubActions(octokit, config, repo);

      // Configure secrets if API key provided
      if (config.secrets && config.secrets.easyrouterApiKey) {
        await configureGitHubSecrets(octokit, config, repo);
      }
      sendProgress('progress-actions', 'GitHub Actions 配置成功 ✓', 'complete');

      // Step 4: Enable GitHub Pages
      sendProgress('progress-pages', '正在启用 GitHub Pages...', 'in-progress');
      await enableGitHubPages(octokit, config, repo);
      sendProgress('progress-pages', 'GitHub Pages 启用成功 ✓', 'complete');
      sendProgress('progress-pages', '提示：GitHub Pages 首次构建需要 1-2 分钟，请稍候再访问网站', 'info');

      // Step 5: Complete
      sendProgress('progress-complete', '正在完成部署...', 'in-progress');
      await new Promise(resolve => setTimeout(resolve, 500));
      sendProgress('progress-complete', '部署完成！✓', 'complete');

      // Send completion event
      if (mainWindow) {
        mainWindow.webContents.send('deploy-complete', {
          success: true,
          siteUrl: `https://${config.github.username}.github.io/${config.github.repoName}`,
          repoUrl: `https://github.com/${config.github.username}/${config.github.repoName}`
        });
      }

      return { success: true };

    } catch (error) {
      console.error('Deployment failed:', error);

      if (mainWindow) {
        mainWindow.webContents.send('deploy-error', {
          success: false,
          error: error.message,
          details: error.stack
        });
      }

      return {
        success: false,
        error: error.message
      };
    }
  });
}

function sendProgress(stepId, message, status) {
  if (mainWindow) {
    mainWindow.webContents.send('deploy-progress', {
      stepId,
      message,
      status
    });
  }
}

// ============================================================================
// Deployment Functions
// ============================================================================

async function createRepository(octokit, config) {
  try {
    const { data: repo } = await octokit.rest.repos.createForAuthenticatedUser({
      name: config.github.repoName,
      description: 'AI Daily News - 个性化 AI 新闻聚合器',
      homepage: `https://${config.github.username}.github.io/${config.github.repoName}`,
      private: false,
      has_issues: true,
      has_projects: false,
      has_wiki: false,
      auto_init: false  // Don't auto-init to avoid README conflict
    });

    // Wait a moment for repository to be ready
    await new Promise(resolve => setTimeout(resolve, 1000));

    return repo;
  } catch (error) {
    if (error.status === 422) {
      throw new Error(`仓库 "${config.github.repoName}" 已存在，请选择其他名称`);
    }
    throw error;
  }
}

async function uploadProjectFiles(octokit, config, repo) {
  const projectRoot = path.join(__dirname, '..');

  // Create initial commit to establish main branch
  const initialReadme = generateReadme(config);

  try {
    // Create README.md as the first commit
    await octokit.rest.repos.createOrUpdateFileContents({
      owner: config.github.username,
      repo: config.github.repoName,
      path: 'README.md',
      message: 'feat: initial commit',
      content: Buffer.from(initialReadme).toString('base64'),
      committer: {
        name: config.github.username,
        email: config.github.email
      }
    });

    // Wait for branch to be created
    await new Promise(resolve => setTimeout(resolve, 1000));
  } catch (error) {
    console.error('Failed to create initial commit:', error);
    throw new Error(`创建初始提交失败: ${error.message}`);
  }

  // List of files to upload
  const filesToUpload = [
    // Frontend files
    { path: 'index.html', source: 'index.html', required: true },
    { path: 'assets/styles.css', source: 'assets/styles.css', required: true },
    { path: 'assets/app.js', source: 'assets/app.js', required: true },

    // Python scripts - ensure __init__.py is first to create directory
    { path: 'scripts/__init__.py', content: '# AI News Radar Scripts\n' },
    { path: 'scripts/update_news.py', source: 'scripts/update_news.py', required: true },
    { path: 'scripts/ai_relevance.py', source: 'scripts/ai_relevance.py', required: true },

    // AI Filter modules
    { path: 'scripts/ai_filter/__init__.py', source: 'scripts/ai_filter/__init__.py', required: true },
    { path: 'scripts/ai_filter/main_filter.py', source: 'scripts/ai_filter/main_filter.py', required: true },
    { path: 'scripts/ai_filter/whitelist_router.py', source: 'scripts/ai_filter/whitelist_router.py', required: true },
    { path: 'scripts/ai_filter/tier0_processor.py', source: 'scripts/ai_filter/tier0_processor.py', required: true },
    { path: 'scripts/ai_filter/tier1_filter.py', source: 'scripts/ai_filter/tier1_filter.py', required: true },
    { path: 'scripts/ai_filter/tier2_pipeline.py', source: 'scripts/ai_filter/tier2_pipeline.py', required: true },
    { path: 'scripts/ai_filter/easyrouter_client.py', source: 'scripts/ai_filter/easyrouter_client.py', required: true },
    { path: 'scripts/ai_filter/language_detector.py', source: 'scripts/ai_filter/language_detector.py', required: true },
    { path: 'scripts/ai_filter/prompts.py', source: 'scripts/ai_filter/prompts.py', required: true },

    // Config files
    { path: 'config/source-whitelist.yaml', source: 'config/source-whitelist.yaml', required: true },
    { path: 'config/source-tier-allocation.md', source: 'config/source-tier-allocation.md', required: false },
    { path: 'feeds/follow.opml', content: generateOpml(config) },
    { path: 'requirements.txt', source: 'requirements.txt', required: false },

    // Empty data directory with placeholder
    { path: 'data/.gitkeep', content: '' }
  ];

  for (const file of filesToUpload) {
    try {
      let content;

      if (file.content !== undefined) {
        // Use provided content
        content = file.content;
      } else if (file.source) {
        // Read from project
        content = await readProjectFile(projectRoot, file.source);
        if (!content) {
          if (file.required) {
            throw new Error(`必需文件 ${file.source} 未找到`);
          }
          console.warn(`Skipping ${file.path}: source file not found`);
          continue;
        }
      }

      await octokit.rest.repos.createOrUpdateFileContents({
        owner: config.github.username,
        repo: config.github.repoName,
        path: file.path,
        message: `feat: add ${file.path}`,
        content: Buffer.from(content).toString('base64'),
        committer: {
          name: config.github.username,
          email: config.github.email
        }
      });

      // Rate limiting: wait between file uploads
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      console.error(`Failed to upload ${file.path}:`, error);
      throw new Error(`上传文件 ${file.path} 失败: ${error.message}`);
    }
  }
}

async function readProjectFile(projectRoot, relativePath) {
  try {
    const content = await fs.readFile(path.join(projectRoot, relativePath), 'utf8');
    return content; // Allow empty files
  } catch (error) {
    console.error(`File not found: ${relativePath}`, error.message);
    return null; // Return null to indicate file doesn't exist
  }
}

function generateReadme(config) {
  return `# AI Daily News

个性化 AI 新闻聚合器

## 🌐 在线访问

访问网站：[https://${config.github.username}.github.io/${config.github.repoName}](https://${config.github.username}.github.io/${config.github.repoName})

## 📰 RSS 订阅源

此网站聚合了 ${config.feeds.length} 个 RSS 订阅源的内容。

## 🔄 自动更新

网站通过 GitHub Actions 自动更新，更新计划：${getScheduleDescription(config.settings.updateSchedule)}

## 📝 License

MIT
`;
}

function getScheduleDescription(cron) {
  const scheduleMap = {
    '0 */6 * * *': '每 6 小时',
    '0 */12 * * *': '每 12 小时',
    '0 0 * * *': '每天午夜',
    '0 0 * * 1': '每周一次'
  };
  return scheduleMap[cron] || cron;
}

function generateOpml(config) {
  const feedItems = config.feeds.map(url =>
    `    <outline type="rss" xmlUrl="${url}" />`
  ).join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head>
    <title>AI Daily News Feeds</title>
  </head>
  <body>
${feedItems}
  </body>
</opml>`;
}

async function configureGitHubActions(octokit, config, repo) {
  const workflowContent = generateWorkflowYaml(config);

  await octokit.rest.repos.createOrUpdateFileContents({
    owner: config.github.username,
    repo: config.github.repoName,
    path: '.github/workflows/update-news.yml',
    message: 'feat: add GitHub Actions workflow',
    content: Buffer.from(workflowContent).toString('base64'),
    committer: {
      name: config.github.username,
      email: config.github.email
    }
  });

  await new Promise(resolve => setTimeout(resolve, 1000));
}

function generateWorkflowYaml(config) {
  const hasGlmKey = config.secrets && config.secrets.glmApiKey;
  const hasEasyRouterKey = config.secrets && config.secrets.easyrouterApiKey;

  let envSection = '';
  if (hasGlmKey || hasEasyRouterKey) {
    const envVars = [];
    if (hasGlmKey) envVars.push('          GLM_API_KEY: ${{ secrets.GLM_API_KEY }}');
    if (hasEasyRouterKey) envVars.push('          EASYROUTER_API_KEY: ${{ secrets.EASYROUTER_API_KEY }}');
    envSection = `\n        env:\n${envVars.join('\n')}`;
  }

  return `name: Update News

on:
  schedule:
    - cron: '${config.settings.updateSchedule}'
  workflow_dispatch:
  push:
    branches:
      - main

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install feedparser requests beautifulsoup4 python-dateutil pyyaml

      - name: Update news data${envSection}
        run: |
          python scripts/update_news.py --output-dir data --window-hours 24 --rss-opml feeds/follow.opml

      - name: Commit changes
        run: |
          git config user.name "${config.github.username}"
          git config user.email "${config.github.email}"
          git add data/*.json
          git diff --quiet && git diff --staged --quiet || (git commit -m "chore: update news data" && git push)

  deploy:
    needs: update
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
`;
}

async function enableGitHubPages(octokit, config, repo) {
  try {
    await octokit.rest.repos.createPagesSite({
      owner: config.github.username,
      repo: config.github.repoName,
      source: {
        branch: 'main',
        path: '/'
      }
    });
  } catch (error) {
    if (error.status === 409) {
      // Pages already enabled
      console.log('GitHub Pages already enabled');
    } else {
      throw error;
    }
  }

  await new Promise(resolve => setTimeout(resolve, 1000));
}

async function configureGitHubSecrets(octokit, config, repo) {
  if (!config.secrets) {
    return;
  }

  const { glmApiKey, easyrouterApiKey } = config.secrets;
  if (!glmApiKey && !easyrouterApiKey) {
    return;
  }

  try {
    // Get repository public key for encrypting secrets
    const { data: publicKey } = await octokit.rest.actions.getRepoPublicKey({
      owner: config.github.username,
      repo: config.github.repoName
    });

    // Encrypt secrets using libsodium
    const sodium = require('libsodium-wrappers');
    await sodium.ready;

    const keyBytes = Buffer.from(publicKey.key, 'base64');

    // Configure GLM_API_KEY if provided
    if (glmApiKey) {
      const glmSecretBytes = Buffer.from(glmApiKey);
      const glmEncryptedBytes = sodium.crypto_box_seal(glmSecretBytes, keyBytes);
      const glmEncryptedValue = Buffer.from(glmEncryptedBytes).toString('base64');

      await octokit.rest.actions.createOrUpdateRepoSecret({
        owner: config.github.username,
        repo: config.github.repoName,
        secret_name: 'GLM_API_KEY',
        encrypted_value: glmEncryptedValue,
        key_id: publicKey.key_id
      });

      console.log('GitHub Secret configured: GLM_API_KEY');
    }

    // Configure EASYROUTER_API_KEY if provided
    if (easyrouterApiKey) {
      const erSecretBytes = Buffer.from(easyrouterApiKey);
      const erEncryptedBytes = sodium.crypto_box_seal(erSecretBytes, keyBytes);
      const erEncryptedValue = Buffer.from(erEncryptedBytes).toString('base64');

      await octokit.rest.actions.createOrUpdateRepoSecret({
        owner: config.github.username,
        repo: config.github.repoName,
        secret_name: 'EASYROUTER_API_KEY',
        encrypted_value: erEncryptedValue,
        key_id: publicKey.key_id
      });

      console.log('GitHub Secret configured: EASYROUTER_API_KEY');
    }
  } catch (error) {
    console.error('Failed to configure GitHub Secrets:', error);
    // Don't throw - secrets are optional
  }
}
