/**
 * 设置模态框组件
 */
import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { backendService } from "../lib/api";
import styles from "../page.module.css";

const SettingsModal = ({ isOpen, onClose, user, onLogout }) => {
  const [notificationSettings, setNotificationSettings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [localWebhookUrl, setLocalWebhookUrl] = useState('');
  const [localWebhookSecret, setLocalWebhookSecret] = useState('');
  
  // 防抖定时器
  const webhookUrlTimeoutRef = useRef(null);
  const webhookSecretTimeoutRef = useRef(null);

  // 获取通知设置
  const fetchNotificationSettings = async () => {
    if (!isOpen) return;
    
    setLoading(true);
    try {
      const response = await backendService.notifications.getSettings();
      if (response.status === 0) {
        setNotificationSettings(response.data);
        setLocalWebhookUrl(response.data.webhook?.url || '');
        setLocalWebhookSecret(response.data.webhook?.secret || '');
      }
    } catch (error) {
      console.error('获取通知设置失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 当模态框打开时获取设置
  useEffect(() => {
    if (isOpen) {
      fetchNotificationSettings();
    }
  }, [isOpen]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (webhookUrlTimeoutRef.current) {
        clearTimeout(webhookUrlTimeoutRef.current);
      }
      if (webhookSecretTimeoutRef.current) {
        clearTimeout(webhookSecretTimeoutRef.current);
      }
    };
  }, []);

  // 保存通知设置
  const saveNotificationSettings = async (newSettings) => {
    setSaving(true);
    try {
      const response = await backendService.notifications.updateSettings(newSettings);
      if (response.status === 0) {
        setNotificationSettings(newSettings);
      }
    } catch (error) {
      console.error('保存通知设置失败:', error);
    } finally {
      setSaving(false);
    }
  };

  // 切换邮箱通知
  const toggleEmailNotification = () => {
    if (!notificationSettings) return;
    
    const newSettings = {
      ...notificationSettings,
      email: {
        ...notificationSettings.email,
        enabled: !notificationSettings.email.enabled
      }
    };
    
    saveNotificationSettings(newSettings);
  };

  // 切换Webhook通知
  const toggleWebhookNotification = () => {
    if (!notificationSettings) return;
    
    const newSettings = {
      ...notificationSettings,
      webhook: {
        ...notificationSettings.webhook,
        enabled: !notificationSettings.webhook.enabled
      }
    };
    
    saveNotificationSettings(newSettings);
  };

  // 更新通知等级
  const updateNotifyLevel = (level) => {
    if (!notificationSettings) return;
    
    const newSettings = {
      ...notificationSettings,
      notify_level: parseInt(level)
    };
    
    saveNotificationSettings(newSettings);
  };

  // 更新Webhook URL
  const updateWebhookUrl = (url) => {
    setLocalWebhookUrl(url);
    
    if (webhookUrlTimeoutRef.current) {
      clearTimeout(webhookUrlTimeoutRef.current);
    }
    
    webhookUrlTimeoutRef.current = setTimeout(() => {
      if (!notificationSettings) return;
      
      const newSettings = {
        ...notificationSettings,
        webhook: {
          ...notificationSettings.webhook,
          url: url
        }
      };
      
      saveNotificationSettings(newSettings);
    }, 500); // 500ms防抖
  };

  // 更新Webhook Secret
  const updateWebhookSecret = (secret) => {
    setLocalWebhookSecret(secret);
    
    if (webhookSecretTimeoutRef.current) {
      clearTimeout(webhookSecretTimeoutRef.current);
    }
    
    webhookSecretTimeoutRef.current = setTimeout(() => {
      if (!notificationSettings) return;
      
      const newSettings = {
        ...notificationSettings,
        webhook: {
          ...notificationSettings.webhook,
          secret: secret
        }
      };
      
      saveNotificationSettings(newSettings);
    }, 500); // 500ms防抖
  };

  if (!isOpen) return null;

  return (
    <div className={styles.settingsOverlay} onClick={onClose}>
      <div 
        className={styles.settingsModal} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.settingsHeader}>
          <h2>设置</h2>
          <button 
            className={styles.closeButton}
            onClick={onClose}
          >
            ×
          </button>
        </div>
        
        <div className={styles.settingsContent}>
          <div className={styles.settingsSection}>
            <h3>账户</h3>
            <div className={styles.userInfoSection}>
              <div className={styles.userProfile}>
                <Image
                  src={user?.avatar_url || "/default-avatar.png"}
                  alt={user?.name || "User"}
                  width={48}
                  height={48}
                  className={styles.settingsAvatar}
                />
                <div className={styles.userDetails}>
                  <div className={styles.settingsUserName}>{user?.name}</div>
                  <div className={styles.settingsUserEmail}>{user?.email}</div>
                </div>
              </div>
            </div>
          </div>

          <div className={styles.settingsSection}>
            <h3>通知设置</h3>
            {loading ? (
              <div className={styles.settingsLoading}>加载中...</div>
            ) : notificationSettings ? (
              <div className={styles.notificationSettings}>
                <div className={styles.settingItem}>
                  <div className={styles.settingLabel}>
                    <span>通知等级</span>
                    <small>设置接收通知的最低风险等级</small>
                  </div>
                  <div className={styles.settingControl}>
                    <select
                      value={notificationSettings.notify_level || 0}
                      onChange={(e) => updateNotifyLevel(e.target.value)}
                      disabled={saving}
                      className={styles.notifyLevelSelect}
                    >
                      <option value={0}>普通事件及以上</option>
                      <option value={1}>代码漏洞及以上</option>
                      <option value={2}>安全漏洞及以上</option>
                      <option value={3}>仅信息泄露</option>
                    </select>
                  </div>
                </div>

                <div className={styles.settingItem}>
                  <div className={styles.settingLabel}>
                    <span>邮箱通知</span>
                    <small>接收重要分析结果的邮件通知</small>
                  </div>
                  <div className={styles.settingControl}>
                    <label className={styles.switch}>
                      <input
                        type="checkbox"
                        checked={notificationSettings.email?.enabled || false}
                        onChange={toggleEmailNotification}
                        disabled={saving}
                      />
                      <span className={styles.slider}></span>
                    </label>
                  </div>
                </div>
                
                <div className={styles.settingItem}>
                  <div className={styles.settingLabel}>
                    <span>Webhook通知</span>
                    <small>向外部服务发送通知</small>
                  </div>
                  <div className={styles.settingControl}>
                    <label className={styles.switch}>
                      <input
                        type="checkbox"
                        checked={notificationSettings.webhook?.enabled || false}
                        onChange={toggleWebhookNotification}
                        disabled={saving}
                      />
                      <span className={styles.slider}></span>
                    </label>
                  </div>
                </div>
                
                {notificationSettings.webhook?.enabled && (
                  <div className={styles.webhookConfig}>
                    <div className={styles.webhookField}>
                      <label className={styles.fieldLabel}>Webhook URL</label>
                      <input
                        type="url"
                        value={localWebhookUrl}
                        onChange={(e) => updateWebhookUrl(e.target.value)}
                        disabled={saving}
                        placeholder="https://example.com/webhook"
                        className={styles.webhookInput}
                      />
                    </div>
                    <div className={styles.webhookField}>
                      <label className={styles.fieldLabel}>Webhook Secret</label>
                      <input
                        type="password"
                        value={localWebhookSecret}
                        onChange={(e) => updateWebhookSecret(e.target.value)}
                        disabled={saving}
                        placeholder="输入webhook密钥"
                        className={styles.webhookInput}
                      />
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className={styles.settingsError}>无法加载通知设置</div>
            )}
          </div>

          <div className={styles.settingsSection}>
            <h3>操作</h3>
            <button 
              className={styles.logoutButton}
              onClick={onLogout}
            >
              <span>注销登录</span>
            </button>
          </div>

          <div className={styles.settingsSection}>
            <h3>关于</h3>
            <div className={styles.aboutInfo}>
              <p>Gitlab Reviewer v1.0.0</p>
              <p>智能代码审查工具</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
