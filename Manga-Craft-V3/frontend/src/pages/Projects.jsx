import { useState, useEffect } from 'react';
import { getProjects, createProject, updateProject, deleteProject } from '../services/projectService';
import { useAuth } from '../context/AuthContext';
import ProjectCard from '../components/projects/ProjectCard';
import ProjectForm from '../components/projects/ProjectForm';
import DeleteProjectDialog from '../components/projects/DeleteProjectDialog';
import Modal from '../components/common/Modal';
import Loading from '../components/common/Loading';
import Button from '../components/common/Button';

function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [deletingProject, setDeletingProject] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const { user } = useAuth();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await getProjects();
      setProjects(data);
      setError(null);
    } catch (err) {
      setError('Failed to load projects');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (formData) => {
    setSubmitting(true);
    try {
      // Add user_id from authenticated user
      const projectData = {
        ...formData,
        user_id: user.id,
      };
      
      if (editingProject) {
        await updateProject(editingProject._id, projectData);
      } else {
        await createProject(projectData);
      }
      setShowForm(false);
      setEditingProject(null);
      loadProjects();
    } catch (err) {
      setError(editingProject ? 'Failed to update project' : 'Failed to create project');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setShowForm(true);
  };

  const handleDeleteClick = (project) => {
    setDeletingProject(project);
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    setSubmitting(true);
    try {
      await deleteProject(deletingProject._id);
      setShowDeleteDialog(false);
      setDeletingProject(null);
      loadProjects();
    } catch (err) {
      setError('Failed to delete project');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (project.description && project.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loading size="lg" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Your Projects</h1>
        <p className="text-[var(--text-secondary)]">Every story begins with an idea.</p>
      </div>

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex-1 w-full sm:w-auto">
          <input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
          />
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')} variant="secondary">
            {viewMode === 'grid' ? 'List' : 'Grid'}
          </Button>
          <Button onClick={() => setShowForm(true)}>
            + New Project
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {filteredProjects.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-[var(--text-secondary)] text-lg mb-2">
            {searchQuery ? 'No projects match your search' : 'No projects yet'}
          </p>
          {!searchQuery && (
            <p className="text-[var(--text-secondary)] text-sm">Click "New Project" to create your first manga project</p>
          )}
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project._id}
              project={project}
              onEdit={handleEdit}
              onDelete={handleDeleteClick}
            />
          ))}
        </div>
      )}

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title={editingProject ? 'Edit Project' : 'New Project'}>
        <ProjectForm
          project={editingProject}
          onSubmit={handleSubmit}
          onCancel={() => setShowForm(false)}
          loading={submitting}
        />
      </Modal>

      <Modal isOpen={showDeleteDialog} onClose={() => setShowDeleteDialog(false)} title="Delete Project">
        <DeleteProjectDialog
          project={deletingProject}
          onConfirm={handleDeleteConfirm}
          onCancel={() => setShowDeleteDialog(false)}
          loading={submitting}
        />
      </Modal>
    </div>
  );
}

export default Projects;
