import React, { useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from './ui/button';
import { useDocuments } from '@/hooks/useDocuments';
import { useProjects } from '@/hooks/useProjects';
import { format } from 'date-fns';
import UploadDocumentDialog from './UploadDocumentDialog';

const DocumentList: React.FC = () => {
  const { documents, loading, error, fetchDocuments } = useDocuments();
  const { currentProject } = useProjects();

  useEffect(() => {
    if (currentProject) {
      fetchDocuments(currentProject.id);
    }
  }, [currentProject, fetchDocuments]);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Documents</h2>
        <UploadDocumentDialog>
          <Button>Upload Document</Button>
        </UploadDocumentDialog>
      </div>
      {loading && <p>Loading documents...</p>}
      {error && <p className="text-red-500">{error}</p>}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Discipline</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Last Modified</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((doc) => (
            <TableRow key={doc.id}>
              <TableCell>{doc.name}</TableCell>
              <TableCell>{doc.file_type}</TableCell>
              <TableCell>{doc.discipline}</TableCell>
              <TableCell>{doc.status}</TableCell>
              <TableCell>{format(new Date(doc.updated_at), 'PPP')}</TableCell>
              <TableCell>
                <Button variant="outline" size="sm">
                  View
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default DocumentList;