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
import { useProjects } from '@/hooks/useProjects';
import AddMemberDialog from './AddMemberDialog';

const ProjectMembers: React.FC = () => {
  const {
    currentProject,
    members,
    getProjectMembers,
    removeProjectMember,
    loading,
  } = useProjects();

  useEffect(() => {
    if (currentProject) {
      getProjectMembers(currentProject.id);
    }
  }, [currentProject, getProjectMembers]);

  const handleRemoveMember = (userId: string) => {
    if (currentProject) {
      removeProjectMember(currentProject.id, userId);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Members</h2>
        <AddMemberDialog>
          <Button>Add Member</Button>
        </AddMemberDialog>
      </div>
      {loading && <p>Loading members...</p>}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {members.map((member) => (
            <TableRow key={member.id}>
              <TableCell>{member.user.name}</TableCell>
              <TableCell>{member.user.email}</TableCell>
              <TableCell>{member.role}</TableCell>
              <TableCell>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleRemoveMember(member.user_id)}
                >
                  Remove
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default ProjectMembers;