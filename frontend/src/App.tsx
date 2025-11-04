import { BrowserRouter as Router, Route, Routes, useParams } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import DocumentEditorPage from './pages/DocumentEditorPage';
import WorkflowPage from './pages/WorkflowPage';
import Layout from './components/Layout';
import { ProjectManagement } from './components/ProjectManagement';
import { DocumentUpload } from './components/DocumentUpload';
import { Dashboard } from './components/Dashboard';

// Wrapper component to extract projectId from URL params
function DashboardWrapper() {
  const { projectId } = useParams<{ projectId: string }>();
  return <Dashboard projectId={projectId || 'default-project-id'} />;
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ProjectManagement />} />
          <Route path="/upload" element={<DocumentUpload projectId="test-project-id" />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="/projects/:projectId/dashboard" element={<DashboardWrapper />} />
          <Route path="/dashboard" element={<Dashboard projectId="default-project-id" />} />
          <Route path="/documents/:id/edit" element={<DocumentEditorPage />} />
          <Route path="/workflows" element={<WorkflowPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;