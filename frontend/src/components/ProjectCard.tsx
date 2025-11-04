import React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from './ui/button';
import { Project } from '../store/projects.store';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';

interface ProjectCardProps {
  project: Project;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const navigate = useNavigate();

  const handleViewProject = () => {
    navigate(`/projects/${project.id}`);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
        <CardDescription>{project.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-500">
          Last Modified: {format(new Date(project.updated_at), 'PPP')}
        </p>
      </CardContent>
      <CardFooter>
        <Button variant="outline" onClick={handleViewProject}>
          View Project
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ProjectCard;