/**
 * 设置模态框组件
 */
import Image from "next/image";
import styles from "../page.module.css";

const SettingsModal = ({ isOpen, onClose, user, onLogout }) => {
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
