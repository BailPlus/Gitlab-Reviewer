"use client";

import { useEffect, useState } from "react";
import styles from "./page.module.css";
import Image from "next/image";

// Helper function to get a cookie by name
const getCookie = (name) => {
  if (typeof window === "undefined") {
    return null;
  }
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
};

export default function Home() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDetails, setProjectDetails] = useState(null);
  const [commits, setCommits] = useState([]);
  const [branches, setBranches] = useState([]);
  const [mergeRequests, setMergeRequests] = useState([]);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [typedText, setTypedText] = useState("");
  const fullTitle = "Gitlab-Reviewer";

  useEffect(() => {
    const fetchUserAndProjects = async () => {
      const token = getCookie("token");
      if (token) {
        try {
          const userResponse = await fetch(
            `${process.env.NEXT_PUBLIC_GITLAB_BASE_URL}/api/v4/user`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (userResponse.ok) {
            const userData = await userResponse.json();
            setUser(userData);

            const projectsResponse = await fetch(
              `${process.env.NEXT_PUBLIC_GITLAB_BASE_URL}/api/v4/projects`,
              {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              }
            );

            if (projectsResponse.ok) {
              const projectsData = await projectsResponse.json();
              setProjects(projectsData);
            } else {
              console.error("Failed to fetch projects");
              setProjects([]);
            }
          } else {
            setUser(null);
            setProjects([]);
          }
        } catch (error) {
          console.error("Failed to fetch data:", error);
          setUser(null);
          setProjects([]);
        }
      } else {
        setUser(null);
        setProjects([]);
      }
      setLoading(false);
    };

    fetchUserAndProjects();
  }, []);

  useEffect(() => {
    if (!loading && !user) {
      let i = 0;
      setTypedText(""); // Reset on trigger
      const interval = setInterval(() => {
        setTypedText(fullTitle.substring(0, i + 1));
        i++;
        if (i >= fullTitle.length) {
          clearInterval(interval);
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, [loading, user]);

    const handleLogin = () => {
    const clientId = process.env.NEXT_PUBLIC_CLIENT_ID;
    const redirectUri = process.env.NEXT_PUBLIC_REDIRECT_URI;
    const gitlabBaseUrl = process.env.NEXT_PUBLIC_GITLAB_BASE_URL;
    const scope = process.env.NEXT_PUBLIC_GITLAB_SCOPE;

    const authorizeUrl = `${gitlabBaseUrl}/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;

    window.location.href = authorizeUrl;
  };

  // 获取项目详细信息
  const fetchProjectDetails = async (project) => {
    const token = getCookie("token");
    if (!token) return;

    setLoadingDetails(true);
    setSelectedProject(project);

    try {
      // 获取项目详情
      const projectResponse = await fetch(
        `${process.env.NEXT_PUBLIC_GITLAB_BASE_URL}/api/v4/projects/${project.id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (projectResponse.ok) {
        const projectData = await projectResponse.json();
        setProjectDetails(projectData);
      }

      // 获取提交记录
      const commitsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_GITLAB_BASE_URL}/api/v4/projects/${project.id}/repository/commits?per_page=20`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (commitsResponse.ok) {
        const commitsData = await commitsResponse.json();
        setCommits(commitsData);
      }

      // 获取分支信息
      const branchesResponse = await fetch(
        `${process.env.NEXT_PUBLIC_GITLAB_BASE_URL}/api/v4/projects/${project.id}/repository/branches?per_page=10`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (branchesResponse.ok) {
        const branchesData = await branchesResponse.json();
        setBranches(branchesData);
      }

      // 获取合并请求
      const mrResponse = await fetch(
        `${process.env.NEXT_PUBLIC_GITLAB_BASE_URL}/api/v4/projects/${project.id}/merge_requests?state=all&per_page=10`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (mrResponse.ok) {
        const mrData = await mrResponse.json();
        setMergeRequests(mrData);
      }

    } catch (error) {
      console.error("Failed to fetch project details:", error);
    } finally {
      setLoadingDetails(false);
    }
  };

  // 注销功能
  const handleLogout = async () => {
    try {
      const response = await fetch('/_/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // 清除本地状态和 cookie
      document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      setUser(null);
      setProjects([]);
      setSelectedProject(null);
      setProjectDetails(null);
      setCommits([]);
      setBranches([]);
      setMergeRequests([]);
      setShowSettings(false);
      
      // 重新加载页面以确保完全清理
      window.location.reload();
    } catch (error) {
      console.error('Logout failed:', error);
      // 即使请求失败也清除本地状态
      document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      window.location.reload();
    }
  };

  // 切换设置弹窗
  const toggleSettings = () => {
    setShowSettings(!showSettings);
  };

  return (
    <div className={styles.containerWrapper}>
      {!loading && !user && (
        <div className={styles.loginOverlay}>
          <div className={styles.backgroundGradient}></div>
          <div className={styles.loginContent}>
            <h1 className={styles.projectTitle}>
              {typedText}
              <span className={styles.cursor}></span>
            </h1>
            <button onClick={handleLogin} className={styles.loginButtonLarge}>
              <Image
                src="/gitlab-logo.svg"
                alt="GitLab Logo"
                width={24}
                height={24}
              />
              <span>使用 GitLab 登录</span>
            </button>
          </div>
        </div>
      )}

      <div
        className={`${styles.container} ${
          !loading && !user ? styles.blurred : ""
        }`}
      >
        <aside className={styles.sidebar}>
          <div>
            {loading || !user ? (
              <div className={styles.profile}>
                <div
                  className={`${styles.skeleton} ${styles.skeletonAvatar}`}
                ></div>
                <div className={styles.userInfo}>
                  <div className={`${styles.skeleton} ${styles.skeletonText}`}></div>
                  <div
                    className={`${styles.skeleton} ${styles.skeletonTextShort}`}
                  ></div>
                </div>
              </div>
            ) : (
              <div className={styles.profile}>
                <Image
                  src={user.avatar_url || "/default-avatar.png"}
                  alt={user.name}
                  width={40}
                  height={40}
                  className={styles.avatar}
                />
                <div className={styles.userInfo}>
                  <span className={styles.userName}>{user.name}</span>
                  <span className={styles.userUsername}>@{user.username}</span>
                  <span className={styles.userEmail}>{user.email}</span>
                </div>
              </div>
            )}
            <nav className={styles.repoNav}>
              <h2 className={styles.repoTitle}>仓库列表</h2>
              <ul className={styles.repoList}>
                {loading || !user ? (
                  <>
                    <li
                      className={`${styles.skeleton} ${styles.skeletonRepoItem}`}
                    ></li>
                    <li
                      className={`${styles.skeleton} ${styles.skeletonRepoItem}`}
                    ></li>
                    <li
                      className={`${styles.skeleton} ${styles.skeletonRepoItem}`}
                    ></li>
                  </>
                ) : (
                  projects.map((project) => (
                    <li 
                      key={project.id} 
                      className={`${styles.repoItem} ${
                        selectedProject?.id === project.id ? styles.repoItemSelected : ""
                      }`}
                      onClick={() => fetchProjectDetails(project)}
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
              <div
                className={`${styles.skeleton} ${styles.skeletonSettings}`}
              ></div>
            ) : (
              <button 
                className={styles.settingsButton}
                onClick={toggleSettings}
              >
                <span>设置</span>
              </button>
            )}
          </div>
        </aside>
        <main className={styles.main}>
          <div className={styles.mainContent}>
            {!selectedProject ? (
              <div className={styles.placeholder}>
                <h1>选择一个仓库进行分析</h1>
              </div>
            ) : loadingDetails ? (
              <div className={styles.loading}>
                <p>加载项目信息中...</p>
              </div>
            ) : (
              <div className={styles.projectDetailsContainer}>
                {/* 项目基本信息 */}
                {projectDetails && (
                  <section className={styles.projectInfo}>
                    <div className={styles.projectHeader}>
                      <h1 className={styles.projectName}>{projectDetails.name}</h1>
                      <div className={styles.projectMeta}>
                        <span className={styles.projectId}>ID: {projectDetails.id}</span>
                        <span className={styles.projectVisibility}>{projectDetails.visibility}</span>
                        <span className={styles.projectLanguage}>{projectDetails.default_branch}</span>
                      </div>
                    </div>
                    {projectDetails.description && (
                      <p className={styles.projectDescription}>{projectDetails.description}</p>
                    )}
                    <div className={styles.projectStats}>
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Stars</span>
                        <span className={styles.statValue}>{projectDetails.star_count}</span>
                      </div>
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Forks</span>
                        <span className={styles.statValue}>{projectDetails.forks_count}</span>
                      </div>
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Issues</span>
                        <span className={styles.statValue}>{projectDetails.open_issues_count}</span>
                      </div>
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Created</span>
                        <span className={styles.statValue}>
                          {new Date(projectDetails.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </section>
                )}

                {/* 分支信息 */}
                <section className={styles.branchesSection}>
                  <h2 className={styles.sectionTitle}>分支信息</h2>
                  <div className={styles.branchesList}>
                    {branches.map((branch) => (
                      <div key={branch.name} className={styles.branchItem}>
                        <span className={styles.branchName}>{branch.name}</span>
                        {branch.protected && <span className={styles.branchProtected}>Protected</span>}
                        {branch.default && <span className={styles.branchDefault}>Default</span>}
                      </div>
                    ))}
                  </div>
                </section>

                {/* 最近提交 */}
                <section className={styles.commitsSection}>
                  <h2 className={styles.sectionTitle}>最近提交</h2>
                  <div className={styles.commitsList}>
                    {commits.map((commit) => (
                      <div key={commit.id} className={styles.commitItem}>
                        <div className={styles.commitHeader}>
                          <span className={styles.commitMessage}>{commit.title}</span>
                          <span className={styles.commitId}>{commit.short_id}</span>
                        </div>
                        <div className={styles.commitMeta}>
                          <span className={styles.commitAuthor}>{commit.author_name}</span>
                          <span className={styles.commitDate}>
                            {new Date(commit.created_at).toLocaleString()}
                          </span>
                        </div>
                        {commit.message !== commit.title && (
                          <p className={styles.commitDescription}>{commit.message}</p>
                        )}
                        <div className={styles.commitStats}>
                          <span>+{commit.stats?.additions || 0}</span>
                          <span>-{commit.stats?.deletions || 0}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* 合并请求 */}
                <section className={styles.mergeRequestsSection}>
                  <h2 className={styles.sectionTitle}>合并请求</h2>
                  <div className={styles.mergeRequestsList}>
                    {mergeRequests.map((mr) => (
                      <div key={mr.id} className={styles.mergeRequestItem}>
                        <div className={styles.mrHeader}>
                          <span className={styles.mrTitle}>{mr.title}</span>
                          <span className={`${styles.mrState} ${styles[`mrState${mr.state}`]}`}>
                            {mr.state}
                          </span>
                        </div>
                        <div className={styles.mrMeta}>
                          <span className={styles.mrAuthor}>{mr.author.name}</span>
                          <span className={styles.mrBranch}>
                            {mr.source_branch} → {mr.target_branch}
                          </span>
                          <span className={styles.mrDate}>
                            {new Date(mr.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        {mr.description && (
                          <p className={styles.mrDescription}>{mr.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* 设置弹窗 */}
      {showSettings && (
        <div className={styles.settingsOverlay} onClick={toggleSettings}>
          <div 
            className={styles.settingsModal} 
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.settingsHeader}>
              <h2>设置</h2>
              <button 
                className={styles.closeButton}
                onClick={toggleSettings}
              >
                ×
              </button>
            </div>
            
            <div className={styles.settingsContent}>
              <div className={styles.settingsSection}>
                <h3>账户</h3>
                <div className={styles.userInfoSection}>
                  <div className={styles.userProfile}>
                    <Image
                      src={user?.avatar_url || "/default-avatar.png"}
                      alt={user?.name || "User"}
                      width={48}
                      height={48}
                      className={styles.settingsAvatar}
                    />
                    <div className={styles.userDetails}>
                      <div className={styles.settingsUserName}>{user?.name}</div>
                      <div className={styles.settingsUserEmail}>{user?.email}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className={styles.settingsSection}>
                <h3>操作</h3>
                <button 
                  className={styles.logoutButton}
                  onClick={handleLogout}
                >
                  <span>注销登录</span>
                </button>
              </div>

              <div className={styles.settingsSection}>
                <h3>关于</h3>
                <div className={styles.aboutInfo}>
                  <p>Gitlab Reviewer v1.0.0</p>
                  <p>智能代码审查工具</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
