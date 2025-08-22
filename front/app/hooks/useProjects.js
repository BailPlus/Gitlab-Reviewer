/**
 * 项目相关的自定义Hook
 */
import { useState, useEffect } from 'react';
import { gitlabService } from '../lib/api';

export const useProjects = (user) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProjects = async () => {
    if (!user) {
      setProjects([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const projectsData = await gitlabService.getProjects();
      setProjects(projectsData);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      setError(error.message);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [user]);

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
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
      // 并行获取项目详细信息
      const [projectData, commitsData, branchesData, mrData] = await Promise.all([
        gitlabService.getProject(project.id),
        gitlabService.getProjectCommits(project.id),
        gitlabService.getProjectBranches(project.id),
        gitlabService.getMergeRequests(project.id),
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
