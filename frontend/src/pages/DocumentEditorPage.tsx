import React from 'react';
import { useParams } from 'react-router-dom';

const DocumentEditorPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Document Editor {id}</h1>
      {/* Add document editor here */}
    </div>
  );
};

export default DocumentEditorPage;