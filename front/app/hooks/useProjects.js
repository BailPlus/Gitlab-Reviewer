/**
 * 项目相关的自定义Hook
 */
import { useState, useEffect } from 'react';
import { gitlabService, backendService } from '../lib/api';

export const useProjects = (user) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  const fetchProjects = async () => {
    if (!user) {
      setProjects([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const response = await backendService.repositories.getBoundRepositories();
      if (response.status === 0 && response.data) {
        const boundReposInfo = response.data;
        
        if (boundReposInfo.length > 0) {
          const repoDetailsPromises = boundReposInfo.map(repo => 
            gitlabService.getProject(repo.id)
          );
          const gitlabRepos = await Promise.all(repoDetailsPromises);

          const mergedProjects = gitlabRepos.map(gitlabRepo => {
            const boundInfo = boundReposInfo.find(b => b.id === gitlabRepo.id);
            return {
              ...gitlabRepo,
              analysis_id: boundInfo ? boundInfo.analysis_id : null,
            };
          });
          setProjects(mergedProjects);
          // 默认选中第一个项目
          if (mergedProjects.length > 0 && !selectedProject) {
            setSelectedProject(mergedProjects[0]);
          }
        } else {
          setProjects([]);
          setSelectedProject(null);
        }
      } else {
        setProjects([]);
        setSelectedProject(null);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
      setProjects([]);
      setSelectedProject(null);
    } finally {
      setLoading(false);
    }
  };

  const clearProject = () => {
    setSelectedProject(null);
  };

  useEffect(() => {
    fetchProjects();
  }, [user]);

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
    selectedProject,
    setSelectedProject,
    clearProject,
  };
};

export const useProjectDetails = () => {
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDetails, setProjectDetails] = useState(null);
  const [commits, setCommits] = useState([]);
  const [branches, setBranches] = useState([]);
  const [mergeRequests, setMergeRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProjectDetails = async (project) => {
    if (!project) return;

    setLoading(true);
    setSelectedProject(project);
    setError(null);

    try {
      // 直接使用项目ID获取详细信息（因为project已经包含完整信息）
      const projectId = project.id;

      // 并行获取项目详细信息
      const [projectData, commitsData, branchesData, mrData] = await Promise.all([
        gitlabService.getProject(projectId),
        gitlabService.getProjectCommits(projectId),
        gitlabService.getProjectBranches(projectId),
        gitlabService.getMergeRequests(projectId),
      ]);

      setProjectDetails(projectData);
      setCommits(commitsData);
      setBranches(branchesData);
      setMergeRequests(mrData);
    } catch (error) {
      console.error('Failed to fetch project details:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const clearProject = () => {
    setSelectedProject(null);
    setProjectDetails(null);
    setCommits([]);
    setBranches([]);
    setMergeRequests([]);
    setError(null);
  };

  return {
    selectedProject,
    projectDetails,
    commits,
    branches,
    mergeRequests,
    loading,
    error,
    fetchProjectDetails,
    clearProject,
  };
};

// 仓库绑定相关Hook
export const useRepositoryBinding = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const bindRepository = async (repoId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await backendService.repositories.bindRepository(repoId);
      if (response.status === 0) {
        return true;
      } else if (response.status === 202) {
        // 处理重复绑定的情况
        setError('你已经绑定过此仓库了');
        return false;
      } else {
        throw new Error(response.info || 'Failed to bind repository');
      }
    } catch (error) {
      console.error('Failed to bind repository:', error);
      if (error.response && error.response.status === 400) {
        setError('你已经绑定过此仓库了');
      } else {
        setError(error.message);
      }
      return false;
    } finally {
      setLoading(false);
    }
  };

  const unbindRepository = async (repoId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await backendService.repositories.unbindRepository(repoId);
      if (response.status === 0) {
        return true;
      } else {
        throw new Error(response.info || 'Failed to unbind repository');
      }
    } catch (error) {
      console.error('Failed to unbind repository:', error);
      setError(error.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const verifyAndGetRepositoryId = async (repoName) => {
    setLoading(true);
    setError(null);

    try {
      // 使用GitLab API验证仓库并获取ID
      const projects = await gitlabService.getProjects({ search: repoName });
      const project = projects.find(p => p.path_with_namespace === repoName);
      
      if (!project) {
        throw new Error('Repository not found or not accessible');
      }
      
      return project.id; // 返回仓库ID
    } catch (error) {
      console.error('Failed to verify repository:', error);
      setError(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    bindRepository,
    unbindRepository,
    verifyAndGetRepositoryId,
  };
};
