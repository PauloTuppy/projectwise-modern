import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useProjects } from '@/hooks/useProjects';
import ProjectMembers from '@/components/ProjectMembers';
import DocumentList from '@/components/DocumentList';

const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { currentProject, loading, error, fetchProjectById } = useProjects();

  useEffect(() => {
    if (id) {
      fetchProjectById(id);
    }
  }, [id, fetchProjectById]);

  if (loading) {
    return <p>Loading project details...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  if (!currentProject) {
    return <p>Project not found.</p>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">{currentProject.name}</h1>
      <p className="text-lg mb-4">{currentProject.description}</p>
      <div className="flex space-x-4">
        <p>Status: {currentProject.status}</p>
        <p>Disciplines: {currentProject.disciplines.join(', ')}</p>
      </div>
      <div className="mt-8">
        <ProjectMembers />
      </div>
      <div className="mt-8">
        <DocumentList />
      </div>
    </div>
  );
};

export default ProjectDetailPage;