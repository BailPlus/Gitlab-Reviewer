"use client";

import { useState, useEffect } from 'react';
import { gitlabService, backendService } from '../lib/api';
import styles from '../page.module.css';

const CommitHistorySidebar = ({ project, onCommitAnalysisClick }) => {
  const [pushEvents, setPushEvents] = useState([]);
  const [commitsData, setCommitsData] = useState({});
  const [mergeRequests, setMergeRequests] = useState([]);
  const [mergeRequestReviews, setMergeRequestReviews] = useState({});
  const [loading, setLoading] = useState(false);
  const [expandedPushes, setExpandedPushes] = useState(new Set());
  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState('');
  const [branchesLoading, setBranchesLoading] = useState(false);

  // 获取分支列表
  const fetchBranches = async () => {
    setBranchesLoading(true);
    try {
      const branchList = await gitlabService.getProjectBranches(project.id, { per_page: 50 });
      setBranches(branchList);
      
      // 默认选择默认分支或第一个分支
      if (branchList.length > 0) {
        const defaultBranch = branchList.find(branch => branch.default) || branchList[0];
        setSelectedBranch(defaultBranch.name);
      }
    } catch (error) {
      console.error('获取分支列表失败:', error);
    } finally {
      setBranchesLoading(false);
    }
  };

  // 获取Merge Request列表
  const fetchMergeRequests = async () => {
    try {
      const mrs = await gitlabService.getMergeRequests(project.id, { 
        state: 'all', 
        per_page: 20,
        order_by: 'created_at',
        sort: 'desc'
      });
      setMergeRequests(mrs);
    } catch (error) {
      console.error('获取Merge Request列表失败:', error);
    }
  };

  // 获取push事件
  useEffect(() => {
    if (project?.id) {
      // 切换仓库时重置状态
      setPushEvents([]);
      setCommitsData({});
      setMergeRequests([]);
      setMergeRequestReviews({});
      setExpandedPushes(new Set());
      setBranches([]);
      setSelectedBranch('');
      
      fetchBranches();
      fetchMergeRequests();
    } else {
      // 如果没有项目，清空状态
      setPushEvents([]);
      setCommitsData({});
      setMergeRequests([]);
      setMergeRequestReviews({});
      setExpandedPushes(new Set());
      setBranches([]);
      setSelectedBranch('');
    }
  }, [project?.id]);

  // 当选择的分支改变时，重新获取提交历史
  useEffect(() => {
    if (project?.id && selectedBranch) {
      setPushEvents([]);
      setCommitsData({});
      setExpandedPushes(new Set());
      fetchPushEvents();
    }
  }, [selectedBranch]);

  const fetchPushEvents = async () => {
    if (!selectedBranch) return;
    
    setLoading(true);
    try {
      const events = await gitlabService.getProjectEvents(project.id, { 
        action: 'pushed', 
        per_page: 20 
      });
      
      // 过滤出有push_data的事件，并且匹配选定的分支
      const validPushEvents = events.filter(event => 
        event.push_data && event.push_data.ref === selectedBranch
      );
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

  const handleBranchChange = (branchName) => {
    setSelectedBranch(branchName);
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

  // 合并推送事件和MR，按时间排序
  const getCombinedTimeline = () => {
    const timeline = [];
    
    // 添加推送事件
    pushEvents.forEach(pushEvent => {
      timeline.push({
        type: 'push',
        id: `push-${pushEvent.id}`,
        data: pushEvent,
        createdAt: new Date(pushEvent.created_at)
      });
    });
    
    // 添加Merge Request
    mergeRequests.forEach(mr => {
      timeline.push({
        type: 'merge_request',
        id: `mr-${mr.iid}`,
        data: mr,
        createdAt: new Date(mr.created_at)
      });
    });
    
    // 按时间倒序排序
    return timeline.sort((a, b) => b.createdAt - a.createdAt);
  };

  // 获取MR状态颜色
  const getMergeRequestStatusColor = (state) => {
    // 根据MR状态设置颜色
    switch (state) {
      case 'opened': return '#28a745';
      case 'merged': return '#6f42c1';
      case 'closed': return '#6c757d';
      default: return '#6c757d';
    }
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

  // 处理点击 Merge Request，获取并显示MR评估
  const handleMergeRequestClick = async (mr) => {
    if (!onCommitAnalysisClick) return;
    
    try {
      const response = await backendService.mergeRequests.getMergeRequestReview(project.id, mr.iid);
      
      if (response.status === 0) {
        // 传递分析数据给父组件
        onCommitAnalysisClick({
          commitId: `mr-${mr.iid}`,
          commitTitle: mr.title,
          author: mr.author.name,
          createdAt: mr.created_at,
          analysis: response.data,
          isMergeRequest: true,
          mergeRequestIid: mr.iid,
          sourceBranch: mr.source_branch,
          targetBranch: mr.target_branch,
          mergeRequestState: mr.state
        });
      } else {
        console.error('获取MR分析失败:', response.info);
      }
    } catch (error) {
      console.error('获取MR分析失败:', error);
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
      
      {/* 分支选择器 */}
      {branches.length > 0 && (
        <div className={styles.branchSelector}>
          <label className={styles.branchLabel}>分支:</label>
          <select 
            value={selectedBranch}
            onChange={(e) => handleBranchChange(e.target.value)}
            className={styles.branchSelect}
            disabled={branchesLoading}
          >
            {branches.map((branch) => (
              <option key={branch.name} value={branch.name}>
                {branch.name} {branch.default ? '(默认)' : ''}
              </option>
            ))}
          </select>
        </div>
      )}
      
      <div className={styles.commitSidebarContent}>
        {getCombinedTimeline().length === 0 && !loading && (
          <div className={styles.emptyState}>
            <p>暂无提交记录</p>
          </div>
        )}
        
        {getCombinedTimeline().map((item) => {
          if (item.type === 'push') {
            const pushEvent = item.data;
            return (
              <div key={item.id} className={styles.pushEventItem}>
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
            );
          } else if (item.type === 'merge_request') {
            const mr = item.data;
            const statusColor = getMergeRequestStatusColor(mr.state);
            
            return (
              <div key={item.id} className={styles.pushEventItem}>
                <div 
                  className={styles.pushEventHeader}
                  onClick={() => handleMergeRequestClick(mr)}
                >
                  <div className={styles.pushEventInfo}>
                    <div className={styles.pushEventTitle}>
                      <span className={styles.mergeRequestIcon}>📝</span>
                      <strong>{mr.title}</strong>
                    </div>
                    <div className={styles.pushEventMeta}>
                      <span className={styles.author}>{mr.author.name}</span>
                      <span className={styles.pushDate}>{formatDate(mr.created_at)}</span>
                      <span className={styles.mergeRequestBranch}>
                        {mr.source_branch} → {mr.target_branch}
                      </span>
                      <span 
                        className={styles.mergeRequestStatus}
                        style={{ backgroundColor: statusColor }}
                      >
                        {mr.state === 'opened' ? '进行中' : 
                         mr.state === 'merged' ? '已合并' : '已关闭'}
                      </span>
                    </div>
                  </div>
                  <div className={styles.mergeRequestIid}>
                    !{mr.iid}
                  </div>
                </div>
              </div>
            );
          }
          
          return null;
        })}
      </div>
    </div>
  );
};

export default CommitHistorySidebar;
