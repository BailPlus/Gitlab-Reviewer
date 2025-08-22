/**
 * 认证相关的自定义Hook
 */
import { useState, useEffect } from 'react';
import { gitlabService, backendService, apiUtils } from '../lib/api';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 获取用户信息
  const fetchUser = async () => {
    if (!apiUtils.isAuthenticated()) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      setError(null);
      const userData = await gitlabService.getUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setError(error.message);
      setUser(null);
      // 如果获取用户信息失败，可能是token过期，清除认证信息
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
