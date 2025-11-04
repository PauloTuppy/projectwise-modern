import api from './api';
import { Document } from '../store/documents.store';

export const getProjectDocuments = async (projectId: string): Promise<Document[]> => {
  const response = await api.get(`/projects/${projectId}/documents`);
  return response.data;
};

export const uploadDocument = async (
  projectId: string,
  file: File,
  name: string,
  description: string,
  discipline: string
): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('name', name);
  formData.append('description', description);
  formData.append('discipline', discipline);

  const response = await api.post(`/projects/${projectId}/documents`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};