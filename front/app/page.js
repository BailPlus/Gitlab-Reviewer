"use client";

import { useAuth } from "./hooks/useAuth";
import { useProjects } from "./hooks/useProjects";
import { useModal } from "./hooks/useUI";
import LoginOverlay from "./components/LoginOverlay";
import Sidebar from "./components/Sidebar";
import AnalysisResult from "./components/AnalysisResult"; // 导入新组件
import RepositoryBinding from "./components/RepositoryBinding";
import SettingsModal from "./components/SettingsModal";
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

  // 处理项目选择
  const handleProjectSelect = (project) => {
    setSelectedProject(project);
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
            ) : (
              // 如果选中了项目，显示分析结果
              <AnalysisResult 
                analysisId={selectedProject.analysis_id} 
                project={selectedProject}
              />
            )}
          </div>
        </main>
      </div>

      {/* 设置弹窗 */}
      <SettingsModal
        user={user}
        isOpen={settingsModal.isOpen}
        onClose={settingsModal.close}
        onLogout={handleLogout}
      />
    </div>
  );
}
