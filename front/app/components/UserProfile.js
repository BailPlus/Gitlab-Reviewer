/**
 * 用户资料组件
 */
import Image from "next/image";
import styles from "../page.module.css";

const UserProfile = ({ user }) => {
  if (!user) return null;

  return (
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
  );
};

export default UserProfile;
