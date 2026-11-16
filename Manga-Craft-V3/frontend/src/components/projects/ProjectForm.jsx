import { useState } from 'react';
import Button from '../common/Button';

function ProjectForm({ project, onSubmit, onCancel, loading }) {
  const [formData, setFormData] = useState({
    name: project?.name || '',
    description: project?.description || '',
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const newErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
          Project Name <span className="text-red-400">*</span>
        </label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="e.g., Haikyu Story"
          className="w-full px-4 py-3 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)] disabled:opacity-50"
          disabled={loading}
        />
        {errors.name && <p className="text-red-400 text-sm mt-1">{errors.name}</p>}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
          Description
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="e.g., A story about a young volleyball player"
          rows="3"
          className="w-full px-4 py-3 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)] disabled:opacity-50 resize-none"
          disabled={loading}
        />
      </div>
      
      <div className="flex gap-3 pt-2">
        <Button type="submit" loading={loading} className="flex-1">
          {project ? 'Update' : 'Create'}
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={loading} className="flex-1">
          Cancel
        </Button>
      </div>
    </form>
  );
}

export default ProjectForm;
