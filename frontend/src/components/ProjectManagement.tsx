import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';

interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  disciplines: string[];
  created_at: string;
  updated_at: string;
}

interface Member {
  id: string;
  user_id: string;
  role: 'owner' | 'manager' | 'editor' | 'viewer';
  user: {
    id: string;
    email: string;
    name: string;
  };
}

export const ProjectManagement: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [loading, setLoading] = useState(false);

  // Form states
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('viewer');

  // Fetch projects on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  // Fetch members when project selected
  useEffect(() => {
    if (selectedProject) {
      fetchMembers(selectedProject.id);
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/projects');
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      alert('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchMembers = async (projectId: string) => {
    try {
      const response = await axios.get(`/api/v1/projects/${projectId}/members`);
      setMembers(response.data);
    } catch (error) {
      console.error('Error fetching members:', error);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newProjectName.trim()) {
      alert('Project name is required');
      return;
    }

    try {
      const response = await axios.post('/api/v1/projects', {
        name: newProjectName,
        description: newProjectDesc,
        disciplines: []
      });
      
      setProjects([...projects, response.data]);
      setNewProjectName('');
      setNewProjectDesc('');
      setShowCreateForm(false);
      alert('Project created successfully!');
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Failed to create project');
    }
  };

  const handleInviteMember = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProject) return;
    
    if (!inviteEmail.trim()) {
      alert('Email is required');
      return;
    }

    try {
      await axios.post(`/api/v1/projects/${selectedProject.id}/members`, null, {
        params: {
          member_email: inviteEmail,
          role: inviteRole
        }
      });
      
      setInviteEmail('');
      setInviteRole('viewer');
      setShowInviteForm(false);
      
      // Refresh members list
      fetchMembers(selectedProject.id);
      alert('Member invited successfully!');
    } catch (error) {
      console.error('Error inviting member:', error);
      alert('Failed to invite member');
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!selectedProject) return;
    
    if (!window.confirm('Are you sure you want to remove this member?')) {
      return;
    }

    try {
      await axios.delete(`/api/v1/projects/${selectedProject.id}/members/${userId}`);
      fetchMembers(selectedProject.id);
      alert('Member removed!');
    } catch (error) {
      console.error('Error removing member:', error);
      alert('Failed to remove member');
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'owner':
        return 'bg-purple-100 text-purple-800';
      case 'manager':
        return 'bg-blue-100 text-blue-800';
      case 'editor':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Project Management</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Projects List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Projects</h2>
              <Button
                onClick={() => setShowCreateForm(!showCreateForm)}
                size="sm"
              >
                + New
              </Button>
            </div>

            {showCreateForm && (
              <form onSubmit={handleCreateProject} className="mb-4 p-3 bg-gray-50 rounded space-y-2">
                <input
                  type="text"
                  placeholder="Project name"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="w-full border rounded p-2"
                  required
                />
                <textarea
                  placeholder="Description (optional)"
                  value={newProjectDesc}
                  onChange={(e) => setNewProjectDesc(e.target.value)}
                  className="w-full border rounded p-2"
                  rows={2}
                />
                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">
                    Create
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="flex-1 bg-gray-400 hover:bg-gray-500"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            )}

            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {loading ? (
                <p className="text-gray-500 text-center py-4">Loading...</p>
              ) : projects.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No projects yet</p>
              ) : (
                projects.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => setSelectedProject(project)}
                    className={`p-3 rounded cursor-pointer transition ${
                      selectedProject?.id === project.id
                        ? 'bg-blue-100 border-2 border-blue-500'
                        : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    <p className="font-semibold text-sm">{project.name}</p>
                    <p className="text-xs text-gray-600 capitalize">{project.status}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right: Project Details & Members */}
        <div className="lg:col-span-2">
          {selectedProject ? (
            <div className="space-y-4">
              {/* Project Details */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-2xl font-bold mb-2">{selectedProject.name}</h2>
                <p className="text-gray-600 mb-4">
                  {selectedProject.description || 'No description'}
                </p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Status</p>
                    <p className="font-semibold capitalize">{selectedProject.status}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Created</p>
                    <p className="font-semibold">
                      {new Date(selectedProject.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Members */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold">Team Members ({members.length})</h3>
                  <Button
                    onClick={() => setShowInviteForm(!showInviteForm)}
                    size="sm"
                  >
                    + Invite
                  </Button>
                </div>

                {showInviteForm && (
                  <form onSubmit={handleInviteMember} className="mb-4 p-4 bg-gray-50 rounded space-y-2">
                    <input
                      type="email"
                      placeholder="Email address"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      className="w-full border rounded p-2"
                      required
                    />
                    <select
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value)}
                      className="w-full border rounded p-2"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="editor">Editor</option>
                      <option value="manager">Manager</option>
                    </select>
                    <div className="flex gap-2">
                      <Button type="submit" className="flex-1">
                        Send Invite
                      </Button>
                      <Button
                        type="button"
                        onClick={() => setShowInviteForm(false)}
                        className="flex-1 bg-gray-400 hover:bg-gray-500"
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                )}

                {/* Members Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-2">Name</th>
                        <th className="text-left py-2 px-2">Email</th>
                        <th className="text-left py-2 px-2">Role</th>
                        <th className="text-left py-2 px-2">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {members.map((member) => (
                        <tr key={member.id} className="border-b hover:bg-gray-50">
                          <td className="py-2 px-2">{member.user.name}</td>
                          <td className="py-2 px-2">{member.user.email}</td>
                          <td className="py-2 px-2">
                            <span
                              className={`px-2 py-1 rounded text-xs font-semibold ${getRoleBadgeColor(
                                member.role
                              )}`}
                            >
                              {member.role}
                            </span>
                          </td>
                          <td className="py-2 px-2">
                            {member.role !== 'owner' && (
                              <button
                                onClick={() => handleRemoveMember(member.user_id)}
                                className="text-red-500 hover:text-red-700 text-sm"
                              >
                                Remove
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-12 text-center">
              <p className="text-gray-500 text-lg">Select a project to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
