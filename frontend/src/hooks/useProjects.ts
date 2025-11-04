import { useProjectsStore } from '../store/projects.store';

export const useProjects = () => {
  const projects = useProjectsStore((state) => state.projects);
  const currentProject = useProjectsStore((state) => state.currentProject);
  const loading = useProjectsStore((state) => state.loading);
  const error = useProjectsStore((state) => state.error);
  const fetchProjects = useProjectsStore((state) => state.fetchProjects);
  const createProject = useProjectsStore((state) => state.createProject);
  const fetchProjectById = useProjectsStore((state) => state.fetchProjectById);
  const members = useProjectsStore((state) => state.members);
  const getProjectMembers = useProjectsStore((state) => state.getProjectMembers);
  const addProjectMember = useProjectsStore((state) => state.addProjectMember);
  const removeProjectMember = useProjectsStore((state) => state.removeProjectMember);

  return {
    projects,
    currentProject,
    loading,
    error,
    fetchProjects,
    createProject,
    fetchProjectById,
    members,
    getProjectMembers,
    addProjectMember,
    removeProjectMember,
  };
};