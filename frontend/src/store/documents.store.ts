import { create } from 'zustand';
import { getProjectDocuments, uploadDocument } from '../services/documents';

export interface Document {
  id: string;
  name: string;
  description: string | null;
  file_type: string;
  discipline: string | null;
  status: string;
  current_version_id: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

interface DocumentsState {
  documents: Document[];
  loading: boolean;
  error: string | null;
  fetchDocuments: (projectId: string) => Promise<void>;
  uploadDocument: (
    projectId: string,
    file: File,
    name: string,
    description: string,
    discipline: string
  ) => Promise<void>;
}

export const useDocumentsStore = create<DocumentsState>((set) => ({
  documents: [],
  loading: false,
  error: null,
  fetchDocuments: async (projectId) => {
    set({ loading: true, error: null });
    try {
      const documents = await getProjectDocuments(projectId);
      set({ documents, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch documents', loading: false });
    }
  },
  uploadDocument: async (projectId, file, name, description, discipline) => {
    set({ loading: true, error: null });
    try {
      const newDocument = await uploadDocument(
        projectId,
        file,
        name,
        description,
        discipline
      );
      set((state) => ({
        documents: [...state.documents, newDocument],
        loading: false,
      }));
    } catch (error) {
      set({ error: 'Failed to upload document', loading: false });
    }
  },
}));