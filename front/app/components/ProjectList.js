/**
 * 项目列表组件
 */
import styles from "../page.module.css";

const ProjectList = ({ projects, selectedProject, onProjectSelect, loading }) => {
  return (
    <nav className={styles.repoNav}>
      <h2 className={styles.repoTitle}>仓库列表</h2>
      <ul className={styles.repoList}>
        {projects.map((project) => (
          <li 
            key={project.id} 
            className={`${styles.repoItem} ${
              selectedProject?.id === project.id ? styles.repoItemSelected : ""
            }`}
            onClick={() => onProjectSelect(project)}
          >
            {project.name}
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default ProjectList;
