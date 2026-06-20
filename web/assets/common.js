const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('token') || '';
}

function setToken(token) {
  localStorage.setItem('token', token);
}

function clearToken() {
  localStorage.removeItem('token');
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/';
    return false;
  }
  return true;
}

async function api(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${url}`, { ...options, headers });
  if (response.status === 401) {
    clearToken();
    window.location.href = '/';
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    let message = 'Request failed';
    try {
      const error = await response.json();
      message = error.detail || message;
    } catch (_) {}
    throw new Error(message);
  }
  return response.json();
}

async function login(username, password) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  const response = await fetch('/api/token', { method: 'POST', body: formData });
  if (!response.ok) throw new Error('用户名或密码错误');
  const data = await response.json();
  setToken(data.access_token);
  return data;
}

function logout() {
  clearToken();
  window.location.href = '/';
}

function loadScriptOnce(src) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) {
      existing.addEventListener('load', resolve, { once: true });
      if (existing.dataset.loaded === 'true') resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = () => {
      script.dataset.loaded = 'true';
      resolve();
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

function pageShell(activePage, title) {
  return {
    currentUser: {},
    async initShell() {
      if (!requireAuth()) return;
      try {
        this.currentUser = await api('/users/me');
      } catch (_) {}
    },
    logout,
    goPage(href) {
      if (window.location.pathname !== href) {
        window.location.href = href;
      }
    },
    activePage,
    title,
    menuItems: [
      { key: 'dashboard', label: '仪表盘', icon: 'fas fa-tachometer-alt', href: '/web/dashboard.html' },
      { key: 'testcases', label: '测试用例', icon: 'fas fa-file-alt', href: '/web/testcases.html' },
      { key: 'graph', label: '依赖关系图', icon: 'fas fa-project-diagram', href: '/web/graph.html' },
      { key: 'hooks', label: 'Hook 函数', icon: 'fas fa-code', href: '/web/hooks.html' },
      { key: 'execute', label: '执行测试', icon: 'fas fa-play-circle', href: '/web/execute.html' },
      { key: 'reports', label: '测试报告', icon: 'fas fa-chart-bar', href: '/web/reports.html' }
    ]
  };
}

function getCaseIcon(type) {
  const icons = {
    http: 'fas fa-globe text-blue-500',
    HTTP: 'fas fa-globe text-blue-500',
    mysql: 'fas fa-database text-purple-500',
    MySQL: 'fas fa-database text-purple-500',
    MYSQL: 'fas fa-database text-purple-500',
    redis: 'fas fa-server text-red-500',
    Redis: 'fas fa-server text-red-500',
    REDIS: 'fas fa-server text-red-500',
    ws: 'fas fa-link text-green-500',
    WS: 'fas fa-link text-green-500'
  };
  return icons[type] || 'fas fa-file text-gray-500';
}

function getStatusText(status) {
  const texts = { passed: '通过', failed: '失败', skipped: '跳过' };
  return texts[status] || status;
}

function shellTemplate(content, actions = '') {
  return `
    <div class="app-shell">
      <aside class="app-sidebar">
        <div class="sidebar-brand">
          <div class="brand-logo"><i class="fas fa-bolt"></i></div>
          <div class="brand-text"><h1>AuroraTest</h1><p>自动化测试平台</p></div>
        </div>
        <nav class="sidebar-menu">
          <button v-for="item in menuItems" :key="item.key" type="button" @click="goPage(item.href)"
            :class="['sidebar-menu-item', activePage === item.key ? 'active' : '']">
            <span class="sidebar-menu-icon"><i :class="item.icon"></i></span>
            <span class="sidebar-menu-label">{{ item.label }}</span>
          </button>
        </nav>
        <div class="sidebar-user">
          <div class="sidebar-user-info"><div class="sidebar-avatar"><i class="fas fa-user"></i></div><span>{{ currentUser.username || 'admin' }}</span></div>
          <button @click="logout" class="sidebar-logout"><i class="fas fa-sign-out-alt"></i></button>
        </div>
      </aside>
      <section class="app-main">
        <header class="app-header"><h2>{{ title }}</h2><div class="app-actions">${actions}</div></header>
        <main class="app-content">${content}</main>
      </section>
    </div>`;
}
