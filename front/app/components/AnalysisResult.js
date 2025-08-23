"use client";

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import styles from '../page.module.css';
import { LoadingSpinner } from './ui/Skeleton';
import GitLabIcon from './ui/GitLabIcon';

const AnalysisResult = ({ analysisId, project }) => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
    if (analysisId) {
      const fetchAnalysis = async () => {
        setLoading(true);
        setError(null);
        try {
          const res = await fetch(`/api/analysis/${analysisId}`);
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
  }, [analysisId]);

  useEffect(() => {
    if (result) {
      mermaid.run({
        nodes: document.querySelectorAll('.language-mermaid'),
      });
    }
  }, [result]);

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

  return (
    <div className={styles.analysisResult}>
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
            
            // 匹配格式：proto/greeter.proto:1-13 或者 `proto/greeter.proto:1-13`
            const fileReferenceMatch = childText.match(/^`?([^`]+):(\d+(?:-\d+)?)`?$/);
            
            if (fileReferenceMatch && (!href || href === '')) {
              const [, filePath, lineRange] = fileReferenceMatch;
              return <FileReferenceLink filePath={filePath} lineRange={lineRange} />;
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
    </div>
  );
};

export default AnalysisResult;
