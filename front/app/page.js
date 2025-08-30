"use client";

import { useState } from 'react';
import { useAuth } from "./hooks/useAuth";
import { useProjects } from "./hooks/useProjects";
import { useModal } from "./hooks/useUI";
import LoginOverlay from "./components/LoginOverlay";
import Sidebar from "./components/Sidebar";
import AnalysisResult from "./components/AnalysisResult"; // 导入新组件
import CommitHistorySidebar from "./components/CommitHistorySidebar";
import RepositoryBinding from "./components/RepositoryBinding";
import SettingsModal from "./components/SettingsModal";
import RepositorySettingsModal from "./components/RepositorySettingsModal";
import { LoadingSpinner } from "./components/ui/Skeleton";
import styles from "./page.module.css";

export default function Home() {
  // 认证相关状态
  const { user, loading: authLoading, login, logout, isAuthenticated } = useAuth();
  
  // 项目相关状态
  const { 
    projects, 
    loading: projectsLoading, 
    refetch: refetchProjects,
    selectedProject,
    setSelectedProject,
    clearProject,
  } = useProjects(user);
  
  // UI状态
  const settingsModal = useModal();
  const repositorySettingsModal = useModal();

  // 提交分析状态
  const [commitAnalysis, setCommitAnalysis] = useState(null);
  const [showCommitAnalysis, setShowCommitAnalysis] = useState(false);

  // 处理项目选择
  const handleProjectSelect = (project) => {
    // 如果点击的是当前已选中的项目，先设为null再设回来，强制刷新
    if (selectedProject && selectedProject.id === project.id) {
      setSelectedProject(null);
      setTimeout(() => {
        setSelectedProject(project);
      }, 0);
    } else {
      setSelectedProject(project);
    }
  };

  // 处理登出
  const handleLogout = async () => {
    settingsModal.close();
    await logout();
  };

  // 处理仓库绑定成功
  const handleRepositoryBound = () => {
    refetchProjects(); // 重新获取仓库列表
  };

  // 处理仓库解绑成功
  const handleRepositoryUnbound = () => {
    clearProject(); // 清除当前选中的项目
    refetchProjects(); // 重新获取仓库列表
  };

  // 处理添加仓库（取消选中当前项目，显示绑定界面）
  const handleAddRepository = () => {
    clearProject(); // 清除当前选中的项目，这样会显示仓库绑定界面
  };

  // 处理仓库设置
  const handleRepositorySettings = () => {
    repositorySettingsModal.open();
  };

  // 处理分析触发完成
  const handleAnalysisTriggered = () => {
    // 可以在这里添加刷新逻辑，或者显示提示信息
    repositorySettingsModal.close();
  };

  // 处理提交分析点击
  const handleCommitAnalysisClick = (commitData) => {
    setCommitAnalysis(commitData);
    setShowCommitAnalysis(true);
  };

  // 处理返回仓库分析
  const handleBackToRepositoryAnalysis = () => {
    setShowCommitAnalysis(false);
    setCommitAnalysis(null);
    
    // 强制刷新仓库分析 - 先清除项目再重新设置以触发重新渲染
    const currentProject = selectedProject;
    setSelectedProject(null);
    setTimeout(() => {
      setSelectedProject(currentProject);
    }, 0);
  };

  return (
    <div className={styles.containerWrapper}>
      {/* 登录界面 */}
      {!authLoading && !isAuthenticated && (
        <LoginOverlay onLogin={login} />
      )}

      {/* 主界面 */}
      <div
        className={`${styles.container} ${
          !authLoading && !isAuthenticated ? styles.blurred : ""
        }`}
      >
        {/* 侧边栏 */}
        <Sidebar
          user={user}
          projects={projects}
          selectedProject={selectedProject}
          onProjectSelect={handleProjectSelect}
          onAddRepository={handleAddRepository}
          onSettingsClick={settingsModal.open}
          loading={authLoading || projectsLoading}
        />

        {/* 主内容区 */}
        <main className={styles.main}>
          <div className={styles.mainContent}>
            {!selectedProject ? (
              // 如果没有已绑定的项目，显示仓库绑定界面
              <RepositoryBinding onRepositoryBound={handleRepositoryBound} />
            ) : showCommitAnalysis ? (
              // 显示提交分析结果
              <AnalysisResult 
                commitAnalysis={commitAnalysis}
                project={selectedProject}
                onBackToRepository={handleBackToRepositoryAnalysis}
                isCommitAnalysis={true}
              />
            ) : (
              // 如果选中了项目，显示仓库分析结果
              <AnalysisResult 
                analysisId={selectedProject.analysis_id} 
                project={selectedProject}
                onRepositorySettings={handleRepositorySettings}
                isCommitAnalysis={false}
              />
            )}
          </div>
        </main>

        {/* 右侧提交历史栏 */}
        {selectedProject && (
          <CommitHistorySidebar 
            project={selectedProject} 
            onCommitAnalysisClick={handleCommitAnalysisClick}
          />
        )}
      </div>

      {/* 设置弹窗 */}
      <SettingsModal
        user={user}
        isOpen={settingsModal.isOpen}
        onClose={settingsModal.close}
        onLogout={handleLogout}
      />

      {/* 仓库设置弹窗 */}
      <RepositorySettingsModal
        isOpen={repositorySettingsModal.isOpen}
        onClose={repositorySettingsModal.close}
        project={selectedProject}
        onAnalysisTriggered={handleAnalysisTriggered}
        onRepositoryUnbound={handleRepositoryUnbound}
        onRefreshProjects={refetchProjects}
      />
    </div>
  );
}
