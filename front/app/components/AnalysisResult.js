"use client";

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import styles from '../page.module.css';
import { LoadingSpinner } from './ui/Skeleton';

const AnalysisResult = ({ analysisId }) => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
        }}
      >
        {result}
      </ReactMarkdown>
    </div>
  );
};

export default AnalysisResult;
