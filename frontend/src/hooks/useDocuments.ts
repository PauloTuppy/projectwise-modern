import { useDocumentsStore } from '../store/documents.store';

export const useDocuments = () => {
  const documents = useDocumentsStore((state) => state.documents);
  const loading = useDocumentsStore((state) => state.loading);
  const error = useDocumentsStore((state) => state.error);
  const fetchDocuments = useDocumentsStore((state) => state.fetchDocuments);
  const uploadDocument = useDocumentsStore((state) => state.uploadDocument);

  return {
    documents,
    loading,
    error,
    fetchDocuments,
    uploadDocument,
  };
};