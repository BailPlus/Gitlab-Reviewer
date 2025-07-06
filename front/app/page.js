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
    const authorizeUrl =
      `${process.env.NEXT_PUBLIC_GITLAB_BASE_URL}/oauth/authorize` +
      `?client_id=${process.env.NEXT_PUBLIC_CLIENT_ID}` +
      `&redirect_uri=${process.env.NEXT_PUBLIC_REDIRECT_URI}` +
      `&response_type=code` +
      `&scope=${process.env.NEXT_PUBLIC_GITLAB_SCOPE}`;
    window.location.href = authorizeUrl;
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
                    <li key={project.id} className={styles.repoItem}>
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
              <a href="/" target="_blank" rel="noopener noreferrer">
                <span>设置</span>
              </a>
            )}
          </div>
        </aside>
        <main className={styles.main}>
          <div className={styles.mainContent}>
            <div className={styles.placeholder}>
              <h1>选择一个仓库进行分析</h1>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
