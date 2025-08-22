/**
 * 项目详情组件
 */
import RepositorySettings from './RepositorySettings';
import styles from "../page.module.css";

// 项目基本信息组件
const ProjectInfo = ({ project, boundRepository, onRepositoryUnbound }) => {
  if (!project) return null;

  return (
    <section className={styles.projectInfo}>
      <div className={styles.projectHeader}>
        <div className={styles.projectTitleRow}>
          <h1 className={styles.projectName}>{project.name}</h1>
          {boundRepository && (
            <RepositorySettings 
              repository={boundRepository}
              onRepositoryUnbound={onRepositoryUnbound}
            />
          )}
        </div>
        <div className={styles.projectMeta}>
          <span className={styles.projectId}>ID: {project.id}</span>
          <span className={styles.projectVisibility}>{project.visibility}</span>
          <span className={styles.projectLanguage}>{project.default_branch}</span>
        </div>
      </div>
      {project.description && (
        <p className={styles.projectDescription}>{project.description}</p>
      )}
      <div className={styles.projectStats}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Stars</span>
          <span className={styles.statValue}>{project.star_count}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Forks</span>
          <span className={styles.statValue}>{project.forks_count}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Issues</span>
          <span className={styles.statValue}>{project.open_issues_count}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Created</span>
          <span className={styles.statValue}>
            {new Date(project.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </section>
  );
};

// 分支信息组件
const BranchesSection = ({ branches }) => {
  return (
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
  );
};

// 提交记录组件
const CommitsSection = ({ commits }) => {
  return (
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
  );
};

// 合并请求组件
const MergeRequestsSection = ({ mergeRequests }) => {
  return (
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
  );
};

// 主项目详情组件
const ProjectDetails = ({ projectDetails, commits, branches, mergeRequests, boundRepository, onRepositoryUnbound }) => {
  return (
    <div className={styles.projectDetailsContainer}>
      <ProjectInfo 
        project={projectDetails} 
        boundRepository={boundRepository}
        onRepositoryUnbound={onRepositoryUnbound}
      />
      <BranchesSection branches={branches} />
      <CommitsSection commits={commits} />
      <MergeRequestsSection mergeRequests={mergeRequests} />
    </div>
  );
};

export default ProjectDetails;
