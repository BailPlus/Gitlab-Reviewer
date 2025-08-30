"use client";

import { useState, useEffect } from 'react';
import { gitlabService, backendService } from '../lib/api';
import styles from '../page.module.css';

const CommitHistorySidebar = ({ project, onCommitAnalysisClick }) => {
  const [pushEvents, setPushEvents] = useState([]);
  const [commitsData, setCommitsData] = useState({});
  const [loading, setLoading] = useState(false);
  const [expandedPushes, setExpandedPushes] = useState(new Set());

  // 获取push事件
  useEffect(() => {
    if (project?.id) {
      // 切换仓库时重置状态
      setPushEvents([]);
      setCommitsData({});
      setExpandedPushes(new Set());
      
      fetchPushEvents();
    } else {
      // 如果没有项目，清空状态
      setPushEvents([]);
      setCommitsData({});
      setExpandedPushes(new Set());
    }
  }, [project?.id]);

  const fetchPushEvents = async () => {
    setLoading(true);
    try {
      const events = await gitlabService.getProjectEvents(project.id, { 
        action: 'pushed', 
        per_page: 10 
      });
      
      // 过滤出有push_data的事件
      const validPushEvents = events.filter(event => event.push_data);
      setPushEvents(validPushEvents);
      
      // 为每个push事件获取commits
      for (const event of validPushEvents) {
        if (event.push_data.commit_from && event.push_data.commit_to) {
          await fetchCommitsForPush(event);
        }
      }
    } catch (error) {
      console.error('获取push事件失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCommitsForPush = async (pushEvent) => {
    try {
      const { commit_from, commit_to } = pushEvent.push_data;
      const compareResult = await gitlabService.compareCommits(
        project.id, 
        commit_from, 
        commit_to
      );
      
      setCommitsData(prev => ({
        ...prev,
        [pushEvent.id]: compareResult.commits || []
      }));
    } catch (error) {
      console.error(`获取push ${pushEvent.id} 的commits失败:`, error);
    }
  };

  const togglePushExpanded = (pushId) => {
    const newExpanded = new Set(expandedPushes);
    if (newExpanded.has(pushId)) {
      newExpanded.delete(pushId);
    } else {
      newExpanded.add(pushId);
    }
    setExpandedPushes(newExpanded);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCommitMessage = (message) => {
    return message.split('\n')[0]; // 只显示第一行
  };

  // 处理点击 push 事件，获取提交分析
  const handlePushEventClick = async (pushEvent) => {
    if (!onCommitAnalysisClick) return;
    
    try {
      const commitTo = pushEvent.push_data.commit_to;
      const response = await backendService.commits.getCommitReview(commitTo);
      
      if (response.status === 0) {
        // 传递分析数据给父组件
        onCommitAnalysisClick({
          commitId: commitTo,
          commitTitle: pushEvent.push_data.commit_title,
          author: pushEvent.author.name,
          createdAt: pushEvent.created_at,
          analysis: response.data
        });
      } else {
        console.error('获取提交分析失败:', response.info);
      }
    } catch (error) {
      console.error('获取提交分析失败:', error);
    }
  };

  if (!project) {
    return null;
  }

  return (
    <div className={styles.commitSidebar}>
      <div className={styles.commitSidebarHeader}>
        <h3>提交历史</h3>
        {loading && <span className={styles.loadingDot}>●</span>}
      </div>
      
      <div className={styles.commitSidebarContent}>
        {pushEvents.length === 0 && !loading && (
          <div className={styles.emptyState}>
            <p>暂无提交记录</p>
          </div>
        )}
        
        {pushEvents.map((pushEvent) => (
          <div key={pushEvent.id} className={styles.pushEventItem}>
            <div 
              className={styles.pushEventHeader}
              onClick={() => handlePushEventClick(pushEvent)}
            >
              <div className={styles.pushEventInfo}>
                <div className={styles.pushEventTitle}>
                  <span 
                    className={styles.expandIcon}
                    onClick={(e) => {
                      e.stopPropagation();
                      togglePushExpanded(pushEvent.id);
                    }}
                  >
                    {expandedPushes.has(pushEvent.id) ? '▼' : '▶'}
                  </span>
                  <strong>{pushEvent.push_data.commit_title}</strong>
                </div>
                <div className={styles.pushEventMeta}>
                  <span className={styles.author}>{pushEvent.author.name}</span>
                  <span className={styles.pushDate}>{formatDate(pushEvent.created_at)}</span>
                  <span className={styles.branch}>{pushEvent.push_data.ref}</span>
                </div>
              </div>
              <div className={styles.commitCount}>
                {pushEvent.push_data.commit_count} 个提交
              </div>
            </div>
            
            {expandedPushes.has(pushEvent.id) && commitsData[pushEvent.id] && (
              <div className={styles.commitsContainer}>
                {commitsData[pushEvent.id].map((commit) => (
                  <div key={commit.id} className={styles.commitItem}>
                    <div className={styles.commitHash}>
                      {commit.short_id}
                    </div>
                    <div className={styles.commitDetails}>
                      <div className={styles.commitSingleLine}>
                        <span className={styles.commitMessage}>
                          {formatCommitMessage(commit.message)}
                        </span>
                        <span className={styles.commitAuthor}>
                          {commit.author_name}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommitHistorySidebar;
