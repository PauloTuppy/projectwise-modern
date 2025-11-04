import { create } from 'zustand';
import { getProjects, createProject, getProjectById, getProjectMembers, addProjectMember, removeProjectMember } from '../services/projects';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  disciplines: string[];
  created_at: string;
  updated_at: string;
}

export interface ProjectMember {
  id: string;
  user_id: string;
  role: string;
  user: {
    id: string;
    name: string;
    email: string;
  };
}

interface ProjectsState {
  projects: Project[];
  currentProject: Project | null;
  members: ProjectMember[];
  loading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  createProject: (project: { name: string; description: string }) => Promise<void>;
  fetchProjectById: (id: string) => Promise<void>;
  getProjectMembers: (projectId: string) => Promise<void>;
  addProjectMember: (projectId: string, email: string, role: string) => Promise<void>;
  removeProjectMember: (projectId: string, userId: string) => Promise<void>;
}

export const useProjectsStore = create<ProjectsState>((set) => ({
  projects: [],
  currentProject: null,
  members: [],
  loading: false,
  error: null,
  fetchProjects: async () => {
    set({ loading: true, error: null });
    try {
      const projects = await getProjects();
      set({ projects, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch projects', loading: false });
    }
  },
  createProject: async (project) => {
    set({ loading: true, error: null });
    try {
      const newProject = await createProject(project);
      set((state) => ({
        projects: [...state.projects, newProject],
        loading: false,
      }));
    } catch (error) {
      set({ error: 'Failed to create project', loading: false });
    }
  },
  fetchProjectById: async (id) => {
    set({ loading: true, error: null });
    try {
      const project = await getProjectById(id);
      set({ currentProject: project, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch project', loading: false });
    }
  },
  getProjectMembers: async (projectId) => {
    set({ loading: true, error: null });
    try {
      const members = await getProjectMembers(projectId);
      set({ members, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch members', loading: false });
    }
  },
  addProjectMember: async (projectId, email, role) => {
    set({ loading: true, error: null });
    try {
      const { member } = await addProjectMember(projectId, email, role);
      set((state) => ({
        members: [...state.members, member],
        loading: false,
      }));
    } catch (error) {
      set({ error: 'Failed to add member', loading: false });
    }
  },
  removeProjectMember: async (projectId, userId) => {
    set({ loading: true, error: null });
    try {
      await removeProjectMember(projectId, userId);
      set((state) => ({
        members: state.members.filter((member) => member.user_id !== userId),
        loading: false,
      }));
    } catch (error) {
      set({ error: 'Failed to remove member', loading: false });
    }
  },
}));