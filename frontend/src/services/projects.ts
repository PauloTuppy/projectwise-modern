import api from './api';
import { Project, ProjectMember } from '../store/projects.store';

export const getProjects = async (): Promise<Project[]> => {
  const response = await api.get('/projects');
  return response.data;
};

export const getProjectById = async (id: string): Promise<Project> => {
  const response = await api.get(`/projects/${id}`);
  return response.data;
};

export const createProject = async (project: {
  name: string;
  description: string;
}): Promise<Project> => {
  const response = await api.post('/projects', project);
  return response.data;
};

export const getProjectMembers = async (projectId: string): Promise<ProjectMember[]> => {
  const response = await api.get(`/projects/${projectId}/members`);
  return response.data;
};

export const addProjectMember = async (
  projectId: string,
  email: string,
  role: string
): Promise<{ message: string; member: ProjectMember }> => {
  const response = await api.post(`/projects/${projectId}/members?member_email=${email}&role=${role}`);
  return response.data;
};

export const removeProjectMember = async (
  projectId: string,
  userId: string
): Promise<{ message: string }> => {
  const response = await api.delete(`/projects/${projectId}/members/${userId}`);
  return response.data;
};