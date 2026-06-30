export const en = {
  // Common
  common: {
    cancel: 'Cancel',
    retry: 'Retry',
    confirm: 'Confirm',
    delete: 'Delete',
    close: 'Close',
    save: 'Save',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
  },

  // Sidebar
  sidebar: {
    title: 'Deepfind Agent',
    newChat: 'New Chat',
    apiConnected: 'API Connected',
    apiDisconnected: 'API Disconnected',
    apiChecking: 'Checking...',
    searchPlaceholder: 'Search history...',
    noResults: 'No results found',
  },

  // Main Interface
  main: {
    defaultTitle: 'Deepfind Agent',
    exportPDF: 'PDF',
    exportMarkdown: 'Markdown',
    exportHTML: 'HTML',
  },

  // Progress States
  progress: {
    initializing: 'Initializing',
    planning: 'Planning Tasks',
    searching: 'Searching',
    searchComplete: 'Search Complete',
    analyzing: 'Analyzing Content',
    analyzeComplete: 'Analysis Complete',
    writing: 'Writing Report',
    generatingFiles: 'Generating Files',
    completed: 'Completed',
    cancelled: 'Cancelled',
    thinking: 'Thinking...',
  },

  // Tool calls
  tool: {
    search: 'Search',
    scrape: 'Web Scraping',
    analyze: 'Content Analysis',
    report: 'Report Generation',
    visiting: 'Visiting',
    found: 'Found',
    results: 'results',
    pages: 'pages',
    complete: 'Complete',
  },

  // Input Area
  input: {
    placeholder: 'Enter your research topic...',
    send: 'Send',
    sending: 'Sending...',
    tagline: 'Deepfind Agent · Deep Research, Precise Insights',
  },

  // Messages
  message: {
    user: 'You',
    agent: 'Agent',
    welcome: `Hello! I'm DeepFind Agent, your deep research assistant.

Enter a topic you want to research, and I'll help you:
1. Search for relevant information
2. Analyze web content
3. Generate structured reports

You can export reports in Markdown or PDF format.`,
    taskBreakdown: '📋 **Task Breakdown**\n\n',
    searchResults: '🔍 **Search Results**',
    searchResultsCount: 'results',
    error: '❌ **Error**\n\n',
    networkError: `❌ **Network Error**

Cannot connect to the backend service. Please ensure the API server is running.

Run command:
\`\`\`bash
cd ~/Desktop/docs/deepfind-agent
source venv/bin/activate
python api.py\`\`\``,
    connectionLost: '❌ **Connection Lost**\n\nThe connection to the server has been interrupted. Please retry.',
    noResults: 'No search results found. Please try different keywords.',
    analysisFailed: 'Content analysis failed. Please try again later.',
  },

  // Settings
  settings: {
    title: 'Settings',
    language: 'Language',
    chinese: '中文',
    english: 'English',
    theme: 'Theme',
    light: 'Light',
    dark: 'Dark',
    auto: 'System',
    model: 'Model',
    modelDesc: {
      deepseek_reasoner: 'DeepSeek R1 - Deep reasoning, best for complex analysis',
      deepseek_chat: 'DeepSeek V3 - General chat, faster response',
    },
  },
};