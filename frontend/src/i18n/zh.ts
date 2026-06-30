export const zh = {
  // 通用
  common: {
    cancel: '取消',
    retry: '重试',
    confirm: '确认',
    delete: '删除',
    close: '关闭',
    save: '保存',
    loading: '加载中...',
    success: '成功',
    error: '错误',
    warning: '警告',
  },

  // 侧边栏
  sidebar: {
    title: 'Deepfind Agent',
    newChat: '新建对话',
    apiConnected: 'API 已连接',
    apiDisconnected: 'API 未连接',
    apiChecking: '检查中...',
    searchPlaceholder: '搜索历史记录...',
    noResults: '无匹配结果',
  },

  // 主界面
  main: {
    defaultTitle: 'Deepfind Agent',
    exportPDF: 'PDF',
    exportMarkdown: 'Markdown',
    exportHTML: 'HTML',
  },

  // 进度状态
  progress: {
    initializing: '初始化',
    planning: '拆解任务',
    searching: '执行搜索',
    searchComplete: '搜索完成',
    analyzing: '分析内容',
    analyzeComplete: '内容分析完成',
    writing: '撰写报告',
    generatingFiles: '生成文件',
    completed: '完成',
    cancelled: '已取消',
    thinking: '思考中...',
  },

  // 工具调用
  tool: {
    search: '搜索',
    scrape: '网页解析',
    analyze: '内容分析',
    report: '报告生成',
    visiting: '正在访问',
    found: '找到',
    results: '条结果',
    pages: '个网页',
    complete: '完成',
  },

  // 输入区
  input: {
    placeholder: '输入你想调研的主题...',
    send: '发送',
    sending: '发送中...',
    tagline: 'Deepfind Agent · 深度调研，精准洞察',
  },

  // 消息
  message: {
    user: 'You',
    agent: 'Agent',
    welcome: `你好！我是 DeepFind Agent，一个深度调研助手。

请输入你想调研的主题，我会帮你：
1. 搜索相关信息
2. 分析网页内容
3. 生成结构化报告

你可以导出报告为 Markdown 或 PDF 格式。`,
    taskBreakdown: '📋 **任务拆解**\n\n',
    searchResults: '🔍 **搜索结果**',
    searchResultsCount: '条',
    error: '❌ **错误**\n\n',
    networkError: `❌ **网络错误**

无法连接到后端服务，请确保 API 服务已启动。

运行命令：
\`\`\`bash
cd ~/Desktop/docs/deepfind-agent
source venv/bin/activate
python api.py\`\`\``,
    connectionLost: '❌ **连接中断**\n\n与服务器的连接已断开，请重试。',
    noResults: '搜索无结果，请尝试其他关键词',
    analysisFailed: '网页分析失败，请稍后重试',
  },

  // 设置
  settings: {
    title: '设置',
    language: '语言',
    chinese: '中文',
    english: 'English',
    theme: '主题',
    light: '浅色',
    dark: '深色',
    auto: '跟随系统',
    model: '模型',
    modelDesc: {
      deepseek_reasoner: 'DeepSeek R1 - 深度推理模型，适合复杂分析',
      deepseek_chat: 'DeepSeek V3 - 通用对话模型，响应更快',
    },
  },
};