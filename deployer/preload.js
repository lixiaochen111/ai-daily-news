const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // GitHub token verification
  verifyGitHubToken: (token) => ipcRenderer.invoke('verify-github-token', token),

  // Deployment methods
  startDeploy: (config) => ipcRenderer.invoke('start-deploy', config),

  onDeployProgress: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('deploy-progress', subscription);
    return () => ipcRenderer.removeListener('deploy-progress', subscription);
  },

  onDeployComplete: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('deploy-complete', subscription);
    return () => ipcRenderer.removeListener('deploy-complete', subscription);
  },

  onDeployError: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('deploy-error', subscription);
    return () => ipcRenderer.removeListener('deploy-error', subscription);
  },

  // Utility methods
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  getVersion: () => ipcRenderer.invoke('get-version')
});
