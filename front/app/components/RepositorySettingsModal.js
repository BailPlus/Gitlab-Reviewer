"use client";

import { useState, useEffect } from 'react';
import styles from '../page.module.css';
import { backendService } from '../lib/api';
import NewTabIcon from './ui/NewTabIcon';

const RepositorySettingsModal = ({ isOpen, onClose, project, onAnalysisTriggered, onRepositoryUnbound }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUnbinding, setIsUnbinding] = useState(false);
  const [message, setMessage] = useState('');
  const [unbindMessage, setUnbindMessage] = useState('');

  useEffect(() => {
    // 当模态框打开时，重置所有状态，避免显示旧仓库的信息
    if (isOpen) {
      setMessage('');
      setUnbindMessage('');
      setIsAnalyzing(false);
      setIsUnbinding(false);
    }
  }, [isOpen, project]); // 依赖于 isOpen 和 project，确保每次打开或切换项目时都重置

  // 触发仓库分析
  const handleTriggerAnalysis = async () => {
    if (!project) return;
    
    setIsAnalyzing(true);
    setMessage('');
    
    try {
      const response = await backendService.analysis.createAnalysis({
        repo_id: project.id,
        branch: project.default_branch || 'master'
      });
      
      if (response.status === 0) {
        setMessage('分析任务已成功触发！');
        if (onAnalysisTriggered) {
          onAnalysisTriggered();
        }
      } else {
        setMessage(`分析失败: ${response.info}`);
      }
    } catch (error) {
      setMessage(`分析失败: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 解绑仓库
  const handleUnbindRepository = async () => {
    if (!project) return;

    if (!window.confirm(`确定要解绑仓库 "${project.name}" 吗？此操作不可逆。`)) {
      return;
    }

    setIsUnbinding(true);
    setUnbindMessage('');

    try {
      const response = await backendService.repositories.unbindRepository(project.id);
      if (response.status === 0) {
        setUnbindMessage('仓库解绑成功！');
        if (onRepositoryUnbound) {
          onRepositoryUnbound();
        }
        setTimeout(onClose, 1500); // 延迟关闭模态框
      } else {
        setUnbindMessage(`解绑失败: ${response.info}`);
      }
    } catch (error) {
      setUnbindMessage(`解绑失败: ${error.message}`);
    } finally {
      setIsUnbinding(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.settingsOverlay} onClick={onClose}>
      <div className={styles.settingsModal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.settingsHeader}>
          <h2>仓库设置</h2>
          <button className={styles.closeButton} onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className={styles.settingsContent}>
          <div className={styles.projectInfo}>
            <a href={project?.web_url} target="_blank" rel="noopener noreferrer" className={styles.projectTitleLink}>
              <h3>{project?.name}<NewTabIcon className={styles.newTabIcon} /></h3>
            </a>
            <p className={styles.projectBranch}>默认分支: {project?.default_branch || 'master'}</p>
          </div>
          
          <div className={styles.analysisSection}>
            <h4>分析管理</h4>
            <p className={styles.analysisTip}>手动触发仓库代码分析，生成新的分析报告。</p>
            
            <button 
              className={`${styles.triggerAnalysisButton} ${isAnalyzing ? styles.loading : ''}`}
              onClick={handleTriggerAnalysis}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? '分析中...' : '触发分析'}
            </button>
            
            {message && (
              <div className={`${styles.message} ${
                message.includes('成功') ? styles.success : styles.error
              }`}>
                {message}
              </div>
            )}
          </div>

          {/* 解绑仓库区域 */}
          <div className={styles.unbindSection}>
            <h4>危险操作</h4>
            <p className={styles.unbindTip}>解绑仓库将删除所有相关数据，此操作不可逆。</p>
            
            <button
              className={`${styles.unbindButton} ${isUnbinding ? styles.loading : ''}`}
              onClick={handleUnbindRepository}
              disabled={isUnbinding}
            >
              {isUnbinding ? '解绑中...' : '解绑仓库'}
            </button>

            {unbindMessage && (
              <div className={`${styles.message} ${
                unbindMessage.includes('成功') ? styles.success : styles.error
              }`}>
                {unbindMessage}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RepositorySettingsModal;
