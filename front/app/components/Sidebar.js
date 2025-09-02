/**
 * 侧边栏组件
 */
import UserProfile from "./UserProfile";
import { SkeletonProfile, SkeletonRepoList, SkeletonSettings } from "./ui/Skeleton";
import styles from "../page.module.css";

const Sidebar = ({ 
  user, 
  projects, 
  selectedProject, 
  onProjectSelect, 
  onAddRepository, // 新增：处理添加仓库的回调
  onSettingsClick,
  loading 
}) => {
  return (
    <aside className={styles.sidebar}>
      <div>
        {loading || !user ? (
          <SkeletonProfile />
        ) : (
          <UserProfile user={user} />
        )}
        
        <nav className={styles.repoNav}>
          <h2 className={styles.repoTitle}>仓库列表</h2>
          <ul className={styles.repoList}>
            {/* 添加仓库按钮 */}
            {!loading && user && (
              <li 
                className={`${styles.repoItem} ${styles.addRepoItem}`}
                onClick={onAddRepository}
              >
                <span className={styles.addIcon}>+</span>
                <span>添加仓库</span>
              </li>
            )}
            
            {loading || !user ? (
              <SkeletonRepoList />
            ) : (
              projects.map((project) => (
                <li 
                  key={project.id} 
                  className={`${styles.repoItem} ${
                    selectedProject?.id === project.id ? styles.repoItemSelected : ""
                  }`}
                  onClick={() => onProjectSelect(project)}
                >
                  {project.name}
                </li>
              ))
            )}
          </ul>
        </nav>
      </div>
      
      <div className={styles.settings}>
        {loading || !user ? (
          <SkeletonSettings />
        ) : (
          <button 
            className={styles.settingsButton}
            onClick={onSettingsClick}
          >
            <span>设置</span>
          </button>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
