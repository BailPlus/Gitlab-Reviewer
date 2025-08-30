/**
 * 认证相关的自定义Hook
 */
import { useState, useEffect } from 'react';
import { gitlabService, backendService, apiUtils } from '../lib/api';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 获取用户信息（先用 /api/repositories 验证 token 有效性）
  const fetchUser = async () => {
    if (!apiUtils.isAuthenticated()) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      setError(null);

      // 1) 先调用后端 /api/repositories 判断 token 是否有效
      let tokenInvalid = false;
      try {
        const reposResp = await backendService.repositories.getBoundRepositories();
        // 业务状态码 102 判定为无效 token
        if (reposResp && reposResp.status === 102 && reposResp.info === '无效的gitlab token') {
          tokenInvalid = true;
        }
      } catch (err) {
        // 如果 HTTP 401 也视为 token 无效
        if (err.status === 401) {
          tokenInvalid = true;
        } else {
          console.warn('Token validation request failed (non-auth error):', err.message);
        }
      }

      if (tokenInvalid) {
        apiUtils.clearAuth();
        setUser(null);
        setLoading(false);
        return; // 直接返回，显示登录界面
      }

      // 2) token 有效，再调用 GitLab 获取用户信息
      const userData = await gitlabService.getUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setError(error.message);
      setUser(null);
      // 清除可能的失效 token
      apiUtils.clearAuth();
    } finally {
      setLoading(false);
    }
  };

  // 登录
  const login = () => {
    backendService.auth.login();
  };

  // 登出
  const logout = async () => {
    try {
      await backendService.auth.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      // 无论成功失败都清除本地状态
      apiUtils.clearAuth();
      setUser(null);
      window.location.reload();
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return {
    user,
    loading,
    error,
    login,
    logout,
    refetch: fetchUser,
    isAuthenticated: !!user,
  };
};
