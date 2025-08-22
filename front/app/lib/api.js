/**
 * API服务模块
 * 区分GitLab API和后端API调用
 */

// 获取cookie的工具函数
const getCookie = (name) => {
  if (typeof window === "undefined") {
    return null;
  }
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
};

// GitLab API基础URL
const GITLAB_BASE_URL = process.env.NEXT_PUBLIC_GITLAB_BASE_URL;

// 创建通用的请求函数
const createRequest = (baseUrl) => {
  return async (endpoint, options = {}) => {
    const token = getCookie("token");
    const url = `${baseUrl}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  };
};

// GitLab API请求函数
const gitlabApi = createRequest(GITLAB_BASE_URL);

// 后端API请求函数
const backendApi = async (endpoint, options = {}) => {
  const url = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Backend API request failed: ${url}`, error);
    throw error;
  }
};

// GitLab API 服务
export const gitlabService = {
  // 获取用户信息
  getUser: () => gitlabApi('/api/v4/user'),
  
  // 获取项目列表
  getProjects: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return gitlabApi(`/api/v4/projects${queryString ? `?${queryString}` : ''}`);
  },
  
  // 获取项目详情
  getProject: (projectId) => gitlabApi(`/api/v4/projects/${projectId}`),
  
  // 获取项目提交记录
  getProjectCommits: (projectId, params = { per_page: 20 }) => {
    const queryString = new URLSearchParams(params).toString();
    return gitlabApi(`/api/v4/projects/${projectId}/repository/commits?${queryString}`);
  },
  
  // 获取项目分支
  getProjectBranches: (projectId, params = { per_page: 10 }) => {
    const queryString = new URLSearchParams(params).toString();
    return gitlabApi(`/api/v4/projects/${projectId}/repository/branches?${queryString}`);
  },
  
  // 获取合并请求
  getMergeRequests: (projectId, params = { state: 'all', per_page: 10 }) => {
    const queryString = new URLSearchParams(params).toString();
    return gitlabApi(`/api/v4/projects/${projectId}/merge_requests?${queryString}`);
  },
};

// 后端API服务
export const backendService = {
  // 认证相关
  auth: {
    // 登录
    login: () => {
      window.location.href = '/_/auth/login';
    },
    
    // 登出
    logout: () => backendApi('/_/auth/logout', { method: 'POST' }),
    
    // 获取用户信息
    getProfile: () => backendApi('/_/auth/profile'),
  },
  
  // 分析相关API (示例)
  analysis: {
    // 获取项目分析
    getProjectAnalysis: (projectId) => backendApi(`/api/analysis/project/${projectId}`),
    
    // 创建分析任务
    createAnalysis: (data) => backendApi('/api/analysis', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },
};

// 工具函数
export const apiUtils = {
  getCookie,
  
  // 清除认证信息
  clearAuth: () => {
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  },
  
  // 检查是否已登录
  isAuthenticated: () => !!getCookie('token'),
};
