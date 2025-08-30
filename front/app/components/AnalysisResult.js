"use client";

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import styles from '../page.module.css';
import { LoadingSpinner } from './ui/Skeleton';
import GitLabIcon from './ui/GitLabIcon';
import { backendService } from '../lib/api';

const AnalysisResult = ({ analysisId, project, onRepositorySettings, commitAnalysis, onBackToRepository, isCommitAnalysis = false }) => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [currentAnalysisId, setCurrentAnalysisId] = useState(analysisId);
  const [historyLoading, setHistoryLoading] = useState(false);

  // 创建 GitLab 文件链接
  const createGitLabFileLink = (filePath, lineRange) => {
    if (!project || !project.web_url) {
      return '#';
    }
    
    let url = `${project.web_url}/-/blob/${project.default_branch || 'master'}/${filePath}`;
    
    if (lineRange) {
      // 解析行号范围，如 "1-13" 或 "27-34"
      const [start, end] = lineRange.split('-').map(n => parseInt(n.trim()));
      if (start && end) {
        url += `#L${start}-${end}`;
      } else if (start) {
        url += `#L${start}`;
      }
    }
    
    return url;
  };

  // 从 React children 中提取文本内容
  const extractTextFromChildren = (children) => {
    if (typeof children === 'string') {
      return children;
    }
    if (Array.isArray(children)) {
      return children.map(child => extractTextFromChildren(child)).join('');
    }
    if (children?.props?.children) {
      return extractTextFromChildren(children.props.children);
    }
    return '';
  };

  // 处理文件引用的自定义渲染组件
  const FileReferenceLink = ({ filePath, lineRange }) => {
    const gitlabUrl = createGitLabFileLink(filePath, lineRange);
    
    return (
      <a
        href={gitlabUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={styles.fileReferenceLink}
        title={`在 GitLab 中查看 ${filePath}${lineRange ? `:${lineRange}` : ''}`}
      >
        <GitLabIcon size={14} />
        <span className={styles.fileName}>{filePath}</span>
        {lineRange && <span className={styles.lineRange}>:{lineRange}</span>}
      </a>
    );
  };

  useEffect(() => {
    if (!isCommitAnalysis) {
      setCurrentAnalysisId(analysisId);
    }
  }, [analysisId, isCommitAnalysis]);

  // 初始化Mermaid
  useEffect(() => {
    mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
  }, []);

  // 获取分析历史
  useEffect(() => {
    if (project?.id && !isCommitAnalysis) {
      const fetchAnalysisHistory = async () => {
        setHistoryLoading(true);
        try {
          const response = await backendService.analysis.getAnalysisHistory(project.id);
          if (response.status === 0) {
            setAnalysisHistory(response.data.analysis_history || []);
          }
        } catch (error) {
          console.error('获取分析历史失败:', error);
        } finally {
          setHistoryLoading(false);
        }
      };
      fetchAnalysisHistory();
    }
  }, [project?.id, isCommitAnalysis]);

  // 处理提交分析数据
  useEffect(() => {
    if (isCommitAnalysis && commitAnalysis) {
      setLoading(false);
      setError(null);
      
      try {
        const reviewData = JSON.parse(commitAnalysis.analysis.review);
        let resultContent = reviewData.info || '';
        
        // 如果有建议，添加建议部分
        if (reviewData.suggestion && typeof reviewData.suggestion === 'object') {
          resultContent += '\n\n## 修改建议\n\n';
          Object.entries(reviewData.suggestion).forEach(([filePath, content]) => {
            resultContent += `### ${filePath}\n\n\`\`\`\n${content}\n\`\`\`\n\n`;
          });
        }
        
        setResult(resultContent);
      } catch (parseError) {
        console.error('解析提交分析数据失败:', parseError);
        setError('解析分析数据失败');
      }
    }
  }, [isCommitAnalysis, commitAnalysis]);

  useEffect(() => {
    if (currentAnalysisId && !isCommitAnalysis) {
      const fetchAnalysis = async () => {
        setLoading(true);
        setError(null);
        try {
          const res = await fetch(`/api/analysis/${currentAnalysisId}`);
          const data = await res.json();

          if (data.status === 0) {
            setResult(data.data.result);
            mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
          } else if (data.status === 301) {
            setError(data.info);
          } else {
            throw new Error(data.info || '获取分析结果失败');
          }
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };
      fetchAnalysis();
    }
  }, [currentAnalysisId]);

  useEffect(() => {
    if (result) {
      mermaid.run({
        nodes: document.querySelectorAll('.language-mermaid'),
      });
    }
  }, [result]);

  // 渲染分析内容
  const renderContent = () => {
    if (loading) {
      return <LoadingSpinner message="正在加载分析结果..." />;
    }
    if (error) {
      return (
        <div className={styles.analysisStatus}>
          <p>{error}</p>
        </div>
      );
    }
    if (result) {
      return (
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              if (match && match[1] === 'mermaid') {
                return (
                  <div className="language-mermaid" {...props}>
                    {String(children)}
                  </div>
                );
              }
              return !inline && match ? (
                <pre className={styles.codeBlock}>
                  <code className={className} {...props}>
                    {String(children).replace(/\n$/, '')}
                  </code>
                </pre>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
            a({ href, children, ...props }) {
              // 检查是否是文件引用链接
              const childText = extractTextFromChildren(children);
              
              // 匹配格式1: `README.md` 或 `README.md:1-10` (无href或href为空)
              const fileReferenceMatch1 = childText.match(/^`?([^`:]+)(?::(\d+(?:-\d+)?))?`?$/);
              
              // 匹配格式2: [src/config_cache.py:10-70](src/config_cache.py) (有href)
              const fileReferenceMatch2 = childText.match(/^`?([^`:]+):(\d+(?:-\d+)?)`?$/);
              
              if (fileReferenceMatch1 && (!href || href === '')) {
                const [, filePath, lineRange] = fileReferenceMatch1;
                
                // 新规则：如果包含行号，则始终视为文件链接。
                // 如果没有行号，则要求文件名包含'.'或'/'以避免误判。
                if (lineRange || filePath.includes('.') || filePath.includes('/')) {
                  return <FileReferenceLink filePath={filePath} lineRange={lineRange} />;
                }
              }
              
              // 处理有href的情况，链接文本包含行号但href只是文件路径
              if (fileReferenceMatch2 && href && href.trim() !== '') {
                const [, filePath, lineRange] = fileReferenceMatch2;
                // 检查href是否与文件路径匹配（可能只是文件路径部分）
                if (href.includes(filePath) || filePath.includes(href.replace(/^\.?\//, ''))) {
                  return <FileReferenceLink filePath={filePath} lineRange={lineRange} />;
                }
              }
              
              // 普通链接保持默认行为
              return (
                <a href={href} {...props}>
                  {children}
                </a>
              );
            },
          }}
        >
          {result}
        </ReactMarkdown>
      );
    }
    return null;
  };

  return (
    <div className={styles.analysisContainer}>
      {/* 标题栏 */}
      <div className={styles.analysisHeader}>
        <div className={styles.projectInfo}>
          {isCommitAnalysis ? (
            <>
              <h1 className={styles.projectName}>
                提交分析: {commitAnalysis?.commitTitle}
              </h1>
              <p className={styles.projectDescription}>
                提交ID: {commitAnalysis?.commitId} | 作者: {commitAnalysis?.author} | 
                时间: {commitAnalysis?.createdAt ? new Date(commitAnalysis.createdAt).toLocaleString('zh-CN') : ''}
                {commitAnalysis?.analysis?.level !== undefined && (
                  <span className={styles.levelIndicator}>
                    {' | 级别: '}
                    <span className={styles[`level${commitAnalysis.analysis.level}`]}>
                      {['普通事件', '代码漏洞', '安全漏洞', '信息泄露'][commitAnalysis.analysis.level] || '未知'}
                    </span>
                  </span>
                )}
              </p>
            </>
          ) : (
            <>
              <h1 className={styles.projectName}>{project?.name}</h1>
              <p className={styles.projectDescription}>{project?.description || '暂无描述'}</p>
            </>
          )}
        </div>
        <div className={styles.headerActions}>
          {isCommitAnalysis ? (
            <button 
              className={styles.repositorySettingsButton}
              onClick={onBackToRepository}
              title="返回仓库分析"
            >
              <span>← 返回仓库</span>
            </button>
          ) : (
            <>
              {/* 分析历史选择 */}
              {analysisHistory.length > 0 && (
                <div className={styles.analysisSelector}>
                  <label htmlFor="analysis-select">分析版本:</label>
                  <select 
                    id="analysis-select"
                    value={currentAnalysisId || ''}
                    onChange={(e) => setCurrentAnalysisId(parseInt(e.target.value))}
                    className={styles.analysisSelect}
                    disabled={historyLoading}
                  >
                    {analysisHistory.map((id) => (
                      <option key={id} value={id}>
                        分析 #{id} {id === analysisId ? '(最新)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <button 
                className={styles.repositorySettingsButton}
                onClick={onRepositorySettings}
                title="仓库设置"
              >
                <span>设置</span>
              </button>
            </>
          )}
        </div>
      </div>
      
      {/* 分析结果内容 */}
      <div className={styles.analysisResult}>
        {renderContent()}
      </div>
    </div>
  );
};

export default AnalysisResult;
