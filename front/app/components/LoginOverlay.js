/**
 * 登录界面组件
 */
import Image from "next/image";
import { useTypewriter } from "../hooks/useUI";
import styles from "../page.module.css";

const LoginOverlay = ({ onLogin }) => {
  const typedText = useTypewriter("Gitlab-Reviewer", 100, true);

  return (
    <div className={styles.loginOverlay}>
      <div className={styles.backgroundGradient}></div>
      <div className={styles.loginContent}>
        <h1 className={styles.projectTitle}>
          {typedText}
          <span className={styles.cursor}></span>
        </h1>
        <button onClick={onLogin} className={styles.loginButtonLarge}>
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
  );
};

export default LoginOverlay;
