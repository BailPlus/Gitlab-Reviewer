/**
 * 仓库设置组件
 */
import { useState } from 'react';
import { useRepositoryBinding } from '../hooks/useProjects';
import styles from '../page.module.css';

const RepositorySettings = ({ repository, onRepositoryUnbound }) => {
  const [showSettings, setShowSettings] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const { loading, error, unbindRepository } = useRepositoryBinding();

  const handleUnbind = async () => {
    const success = await unbindRepository(repository.id);
    if (success) {
      setShowConfirm(false);
      setShowSettings(false);
      onRepositoryUnbound();
    }
  };

  return (
    <div className={styles.repositorySettings}>
      <button
        className={styles.settingsIconButton}
        onClick={() => setShowSettings(!showSettings)}
        title="仓库设置"
      >
        ⚙️
      </button>

      {showSettings && (
        <div className={styles.settingsDropdown}>
          <div className={styles.settingsMenu}>
            <button
              className={styles.settingsMenuItem}
              onClick={() => setShowConfirm(true)}
            >
              🗑️ 解绑仓库
            </button>
          </div>
        </div>
      )}

      {showConfirm && (
        <div className={styles.confirmOverlay} onClick={() => setShowConfirm(false)}>
          <div 
            className={styles.confirmModal}
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.confirmHeader}>
              <h3>确认解绑仓库</h3>
            </div>
            <div className={styles.confirmContent}>
              <p>确定要解绑仓库 <strong>{repository.name}</strong> 吗？</p>
              <p className={styles.warning}>
                解绑后，您将无法继续对此仓库进行分析，已有的分析数据可能会被保留。
              </p>
            </div>
            <div className={styles.confirmActions}>
              <button
                className={styles.cancelButton}
                onClick={() => setShowConfirm(false)}
                disabled={loading}
              >
                取消
              </button>
              <button
                className={styles.confirmButton}
                onClick={handleUnbind}
                disabled={loading}
              >
                {loading ? '解绑中...' : '确认解绑'}
              </button>
            </div>
            {error && (
              <div className={styles.errorMessage}>
                错误: {error}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RepositorySettings;
