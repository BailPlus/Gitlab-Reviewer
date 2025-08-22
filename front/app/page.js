"use client";

import { useAuth } from "./hooks/useAuth";
import { useProjects, useProjectDetails } from "./hooks/useProjects";
import { useModal } from "./hooks/useUI";
import LoginOverlay from "./components/LoginOverlay";
import Sidebar from "./components/Sidebar";
import ProjectDetails from "./components/ProjectDetails";
import SettingsModal from "./components/SettingsModal";
import { LoadingSpinner } from "./components/ui/Skeleton";
import styles from "./page.module.css";

export default function Home() {
  // 认证相关状态
  const { user, loading: authLoading, login, logout, isAuthenticated } = useAuth();
  
  // 项目相关状态
  const { projects, loading: projectsLoading } = useProjects(user);
  const {
    selectedProject,
    projectDetails,
    commits,
    branches,
    mergeRequests,
    loading: detailsLoading,
    fetchProjectDetails,
  } = useProjectDetails();
  
  // UI状态
  const settingsModal = useModal();

  // 处理项目选择
  const handleProjectSelect = (project) => {
    fetchProjectDetails(project);
  };

  // 处理登出
  const handleLogout = async () => {
    settingsModal.close();
    await logout();
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
          onSettingsClick={settingsModal.open}
          loading={authLoading || projectsLoading}
        />

        {/* 主内容区 */}
        <main className={styles.main}>
          <div className={styles.mainContent}>
            {!selectedProject ? (
              <div className={styles.placeholder}>
                <h1>选择一个仓库进行分析</h1>
              </div>
            ) : detailsLoading ? (
              <LoadingSpinner message="加载项目信息中..." />
            ) : (
              <ProjectDetails
                projectDetails={projectDetails}
                commits={commits}
                branches={branches}
                mergeRequests={mergeRequests}
              />
            )}
          </div>
        </main>
      </div>

      {/* 设置模态框 */}
      <SettingsModal
        isOpen={settingsModal.isOpen}
        onClose={settingsModal.close}
        user={user}
        onLogout={handleLogout}
      />
    </div>
  );
}
