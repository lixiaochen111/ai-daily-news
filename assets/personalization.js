/**
 * PersonalizationEngine
 *
 * 前端个性化评分引擎，支持用户反馈循环和偏好学习
 * 功能：
 * - 计算个性化评分（基于质量分、相关性、分类权重、新鲜度）
 * - 用户反馈循环（感兴趣/不感兴趣）
 * - localStorage持久化存储
 * - 动态重排序
 */

class PersonalizationEngine {
  constructor() {
    this.storageKey = 'ai_news_preferences';
    this.preferences = this.loadPreferences();
    this.initializeDefaultWeights();
  }

  /**
   * 初始化默认权重
   */
  initializeDefaultWeights() {
    if (!this.preferences.categoryWeights) {
      this.preferences.categoryWeights = {
        // 默认权重按SOURCE_KINDS分类
        'official': 1.2,      // 官方源权重高
        'newsletter': 1.1,    // 日报权重较高
        'builders': 1.0,      // Builders中性
        'aggregate': 0.9,     // 聚合源略低
        'blogs': 1.0,         // 博客中性
        'aihub': 0.95,        // AI站点略低
        'default': 1.0        // 默认权重
      };
    }

    if (!this.preferences.siteWeights) {
      this.preferences.siteWeights = {};
    }

    if (!this.preferences.sourceWeights) {
      this.preferences.sourceWeights = {};
    }

    if (!this.preferences.keywordWeights) {
      this.preferences.keywordWeights = {};
    }

    if (!this.preferences.interactionCount === undefined) {
      this.preferences.interactionCount = 0;
    }

    if (!this.preferences.interestedCount === undefined) {
      this.preferences.interestedCount = 0;
    }

    if (!this.preferences.notInterestedCount === undefined) {
      this.preferences.notInterestedCount = 0;
    }
  }

  /**
   * 从localStorage加载偏好
   */
  loadPreferences() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load preferences from localStorage:', error);
    }
    return {};
  }

  /**
   * 保存偏好到localStorage
   */
  savePreferences() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.preferences));
    } catch (error) {
      console.error('Failed to save preferences to localStorage:', error);
    }
  }

  /**
   * 计算个性化评分
   * @param {Object} item - 新闻条目
   * @param {string} tone - 来源类型（从SOURCE_KINDS获取）
   * @returns {number} - 个性化评分
   */
  calculatePersonalizedScore(item, tone = 'default') {
    // 基础质量分（如果存在AI评分）
    const qualityScore = item.quality_score || item.ai_score || 0.5;

    // 相关性分数（如果存在）
    const relevanceScore = item.relevance_score || 1.0;

    // 分类权重（基于tone）
    const categoryWeight = this.preferences.categoryWeights[tone] || 1.0;

    // 站点权重
    const siteWeight = this.preferences.siteWeights[item.site_id] || 1.0;

    // 来源权重（source分区）
    const sourceWeight = this.preferences.sourceWeights[item.source] || 1.0;

    // 关键词权重计算
    let keywordBoost = 1.0;
    const itemText = `${item.title || ''} ${item.title_zh || ''} ${item.title_en || ''}`.toLowerCase();

    for (const [keyword, weight] of Object.entries(this.preferences.keywordWeights)) {
      if (itemText.includes(keyword.toLowerCase())) {
        keywordBoost *= weight;
      }
    }

    // 新鲜度乘数（24小时内的内容）
    const freshnessMultiplier = this.calculateFreshnessMultiplier(item);

    // 综合评分公式
    // score = quality × (0.5 + relevance × 0.5) × categoryWeight × siteWeight × sourceWeight × keywordBoost × freshness
    const personalizedScore =
      qualityScore *
      (0.5 + relevanceScore * 0.5) *
      categoryWeight *
      siteWeight *
      sourceWeight *
      keywordBoost *
      freshnessMultiplier;

    return Math.max(0, Math.min(1, personalizedScore)); // 限制在[0,1]范围
  }

  /**
   * 计算新鲜度乘数
   * @param {Object} item - 新闻条目
   * @returns {number} - 新鲜度乘数
   */
  calculateFreshnessMultiplier(item) {
    const publishedAt = item.published_at || item.first_seen_at;
    if (!publishedAt) return 1.0;

    try {
      const publishedTime = new Date(publishedAt).getTime();
      const now = Date.now();
      const ageHours = (now - publishedTime) / (1000 * 60 * 60);

      // 0-6小时：1.1倍
      // 6-12小时：1.05倍
      // 12-24小时：1.0倍
      // 超过24小时：0.9倍
      if (ageHours < 6) return 1.1;
      if (ageHours < 12) return 1.05;
      if (ageHours < 24) return 1.0;
      return 0.9;
    } catch (error) {
      return 1.0;
    }
  }

  /**
   * 标记为感兴趣
   * @param {Object} item - 新闻条目
   * @param {string} tone - 来源类型
   */
  markInterested(item, tone = 'default') {
    // 增加分类权重
    if (this.preferences.categoryWeights[tone]) {
      this.preferences.categoryWeights[tone] *= 1.1;
      this.preferences.categoryWeights[tone] = Math.min(2.0, this.preferences.categoryWeights[tone]);
    }

    // 增加站点权重
    const currentSiteWeight = this.preferences.siteWeights[item.site_id] || 1.0;
    this.preferences.siteWeights[item.site_id] = Math.min(2.0, currentSiteWeight * 1.1);

    // 增加来源权重
    if (item.source) {
      const currentSourceWeight = this.preferences.sourceWeights[item.source] || 1.0;
      this.preferences.sourceWeights[item.source] = Math.min(2.0, currentSourceWeight * 1.1);
    }

    // 提取并增强关键词权重
    this.extractAndBoostKeywords(item, 1.05);

    // 更新统计
    this.preferences.interactionCount = (this.preferences.interactionCount || 0) + 1;
    this.preferences.interestedCount = (this.preferences.interestedCount || 0) + 1;

    this.savePreferences();
  }

  /**
   * 标记为不感兴趣
   * @param {Object} item - 新闻条目
   * @param {string} tone - 来源类型
   */
  markNotInterested(item, tone = 'default') {
    // 降低分类权重
    if (this.preferences.categoryWeights[tone]) {
      this.preferences.categoryWeights[tone] *= 0.85;
      this.preferences.categoryWeights[tone] = Math.max(0.5, this.preferences.categoryWeights[tone]);
    }

    // 降低站点权重
    const currentSiteWeight = this.preferences.siteWeights[item.site_id] || 1.0;
    this.preferences.siteWeights[item.site_id] = Math.max(0.5, currentSiteWeight * 0.85);

    // 降低来源权重
    if (item.source) {
      const currentSourceWeight = this.preferences.sourceWeights[item.source] || 1.0;
      this.preferences.sourceWeights[item.source] = Math.max(0.5, currentSourceWeight * 0.85);
    }

    // 提取并降低关键词权重
    this.extractAndBoostKeywords(item, 0.95);

    // 更新统计
    this.preferences.interactionCount = (this.preferences.interactionCount || 0) + 1;
    this.preferences.notInterestedCount = (this.preferences.notInterestedCount || 0) + 1;

    this.savePreferences();
  }

  /**
   * 提取关键词并调整权重
   * @param {Object} item - 新闻条目
   * @param {number} multiplier - 权重乘数
   */
  extractAndBoostKeywords(item, multiplier) {
    const text = `${item.title || ''} ${item.title_zh || ''} ${item.title_en || ''}`;

    // 简单分词：提取2-4个字符的中文词和完整英文单词
    const chineseWords = text.match(/[\u4e00-\u9fa5]{2,4}/g) || [];
    const englishWords = text.match(/[A-Za-z]{3,}/g) || [];

    const keywords = [...chineseWords, ...englishWords]
      .map(w => w.toLowerCase())
      .filter(w => w.length >= 2);

    // 更新关键词权重
    keywords.forEach(keyword => {
      const currentWeight = this.preferences.keywordWeights[keyword] || 1.0;
      this.preferences.keywordWeights[keyword] = currentWeight * multiplier;

      // 限制权重范围
      if (this.preferences.keywordWeights[keyword] > 1.5) {
        this.preferences.keywordWeights[keyword] = 1.5;
      }
      if (this.preferences.keywordWeights[keyword] < 0.7) {
        this.preferences.keywordWeights[keyword] = 0.7;
      }
    });
  }

  /**
   * 获取统计信息
   * @returns {Object} - 统计信息
   */
  getStats() {
    return {
      totalInteractions: this.preferences.interactionCount || 0,
      interestedCount: this.preferences.interestedCount || 0,
      notInterestedCount: this.preferences.notInterestedCount || 0,
      categoryWeights: {...this.preferences.categoryWeights},
      topSites: this.getTopWeightedItems(this.preferences.siteWeights, 5),
      topSources: this.getTopWeightedItems(this.preferences.sourceWeights, 5),
      topKeywords: this.getTopWeightedItems(this.preferences.keywordWeights, 10)
    };
  }

  /**
   * 获取权重最高的条目
   * @param {Object} weights - 权重对象
   * @param {number} limit - 限制数量
   * @returns {Array} - 权重最高的条目
   */
  getTopWeightedItems(weights, limit) {
    return Object.entries(weights)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([key, weight]) => ({ key, weight }));
  }

  /**
   * 重置所有偏好
   */
  resetPreferences() {
    this.preferences = {};
    this.initializeDefaultWeights();
    this.savePreferences();
  }

  /**
   * 导出偏好设置（用于调试）
   * @returns {Object} - 偏好设置
   */
  exportPreferences() {
    return JSON.parse(JSON.stringify(this.preferences));
  }

  /**
   * 导入偏好设置（用于调试或迁移）
   * @param {Object} preferences - 偏好设置
   */
  importPreferences(preferences) {
    this.preferences = preferences;
    this.initializeDefaultWeights();
    this.savePreferences();
  }
}

// 如果在浏览器环境中，暴露到全局
if (typeof window !== 'undefined') {
  window.PersonalizationEngine = PersonalizationEngine;
}

// 如果在Node.js环境中，导出模块
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PersonalizationEngine;
}
