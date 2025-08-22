/**
 * 骨架屏组件
 */
import styles from "../../page.module.css";

export const SkeletonProfile = () => (
  <div className={styles.profile}>
    <div className={`${styles.skeleton} ${styles.skeletonAvatar}`}></div>
    <div className={styles.userInfo}>
      <div className={`${styles.skeleton} ${styles.skeletonText}`}></div>
      <div className={`${styles.skeleton} ${styles.skeletonTextShort}`}></div>
    </div>
  </div>
);

export const SkeletonRepoList = () => (
  <>
    <li className={`${styles.skeleton} ${styles.skeletonRepoItem}`}></li>
    <li className={`${styles.skeleton} ${styles.skeletonRepoItem}`}></li>
    <li className={`${styles.skeleton} ${styles.skeletonRepoItem}`}></li>
  </>
);

export const SkeletonSettings = () => (
  <div className={`${styles.skeleton} ${styles.skeletonSettings}`}></div>
);

export const LoadingSpinner = ({ message = "加载中..." }) => (
  <div className={styles.loading}>
    <p>{message}</p>
  </div>
);
