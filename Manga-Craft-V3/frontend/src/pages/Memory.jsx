import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { memoryService } from '../services/memoryService';
import { getProjects } from '../services/projectService';
import { Plus, Search, Filter, Sparkles, BookOpen, Users, FileText, Database, Brain, Heart, Palette, Settings } from 'lucide-react';
import { BorderBeam } from 'border-beam';
import { ThinkingOrb } from 'thinking-orbs';
import { MetalFx } from 'metal-fx';
import Modal from '../components/common/Modal';
import Loading from '../components/common/Loading';
import Button from '../components/common/Button';

function Memory() {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [memoryType, setMemoryType] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [editingMemory, setEditingMemory] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const memoryTypes = [
    { value: 'all', label: 'All', icon: Brain },
    { value: 'character', label: 'Characters', icon: Users },
    { value: 'story', label: 'Story', icon: FileText },
    { value: 'relationship', label: 'Relationships', icon: Users },
    { value: 'design_decision', label: 'Design Decisions', icon: Sparkles },
    { value: 'art_style', label: 'Art Style', icon: Sparkles },
    { value: 'preference', label: 'Preferences', icon: Brain },
    { value: 'panel', label: 'Panels', icon: Database },
    { value: 'generated_reference', label: 'Generated References', icon: Database },
    { value: 'character_reference', label: 'Character References', icon: Database },
    { value: 'other_asset', label: 'Other Assets', icon: Database },
    { value: 'location', label: 'Locations', icon: Database },
    { value: 'note', label: 'Notes', icon: BookOpen },
  ];

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadMemories();
    }
  }, [selectedProject, memoryType]);

  const loadProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
      if (data.length > 0) {
        setSelectedProject(data[0]._id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const loadMemories = async () => {
    if (!selectedProject) return;
    
    try {
      setLoading(true);
      const typeFilter = memoryType === 'all' ? null : memoryType;
      const data = await memoryService.listMemories(selectedProject, typeFilter);
      setMemories(data.memories);
    } catch (err) {
      console.error('Failed to load memories:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!selectedProject || !searchQuery.trim()) {
      loadMemories();
      return;
    }

    try {
      setIsSearching(true);
      const data = await memoryService.searchMemories(selectedProject, searchQuery.trim());
      setMemories(data.memories);
    } catch (err) {
      console.error('Failed to search memories:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSubmit = async (formData) => {
    setSubmitting(true);
    try {
      const memoryData = {
        ...formData,
        project_id: selectedProject,
      };

      if (editingMemory) {
        await memoryService.updateMemory(editingMemory.id, memoryData);
      } else {
        await memoryService.createMemory(memoryData);
      }

      setShowForm(false);
      setEditingMemory(null);
      loadMemories();
    } catch (err) {
      console.error('Failed to save memory:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (memory) => {
    setEditingMemory(memory);
    setShowForm(true);
  };

  const handleDelete = async (memoryId) => {
    if (!confirm('Delete this memory?')) return;

    try {
      await memoryService.deleteMemory(memoryId);
      loadMemories();
    } catch (err) {
      console.error('Failed to delete memory:', err);
    }
  };

  const getMemoryIcon = (type) => {
    const iconMap = {
      character: Users,
      story: FileText,
      relationship: Heart,
      design_decision: Settings,
      art_style: Palette,
      preference: Brain,
      panel: Database,
      generated_reference: Database,
      character_reference: Database,
      other_asset: Database,
      location: Database,
      note: BookOpen,
    };
    const Icon = iconMap[type] || Brain;
    return Icon;
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Project Memory</h1>
        <p className="text-[var(--text-secondary)]">Store characters, story elements, and project context</p>
      </div>

      {/* Project Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">Select Project ({projects.length} projects)</label>
        <div className="flex gap-2 overflow-x-auto scrollbar-thin pb-2">
          {projects.map((project) => (
            <button
              key={project._id}
              onClick={() => setSelectedProject(project._id)}
              className={`px-4 py-2 rounded-lg border whitespace-nowrap transition-all ${
                selectedProject === project._id
                  ? 'bg-[var(--accent)]/10 border-[var(--accent)] text-[var(--accent)]'
                  : 'bg-[var(--bg-surface)] border-[var(--border)] text-[var(--text-primary)] hover:border-[var(--accent)]/50'
              }`}
            >
              {project.name}
            </button>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex-1 w-full sm:w-auto flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-secondary)]" />
            <input
              type="text"
              placeholder="Search memories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-4 py-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
            />
          </div>
          <Button onClick={handleSearch} variant="secondary">
            Search
          </Button>
        </div>
        <div className="flex gap-2">
          <select
            value={memoryType}
            onChange={(e) => setMemoryType(e.target.value)}
            className="px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
          >
            {memoryTypes.map((type) => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Memory
          </Button>
        </div>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <ThinkingOrb state="searching" size={64} dark />
        </div>
      ) : isSearching ? (
        <div className="flex items-center justify-center py-12">
          <ThinkingOrb state="searching" size={64} dark />
        </div>
      ) : memories.length === 0 ? (
        <div className="text-center py-16">
          <Sparkles className="w-16 h-16 text-[var(--text-secondary)] mx-auto mb-4 opacity-50" />
          <p className="text-[var(--text-secondary)] text-lg mb-2">
            {searchQuery ? 'No memories match your search' : 'No memories yet'}
          </p>
          {!searchQuery && (
            <p className="text-[var(--text-secondary)] text-sm">Click "Add Memory" to create your first memory</p>
          )}
        </div>
      ) : (
        /* Memory List */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {memories.map((memory) => {
            const Icon = getMemoryIcon(memory.type);
            return (
              <BorderBeam key={memory.id} size="md" colorVariant="mono" strength={0.5}>
                <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-5 h-full">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-[var(--accent)]/10 rounded-lg">
                        <Icon className="w-4 h-4 text-[var(--accent)]" />
                      </div>
                      <span className="text-xs font-medium text-[var(--text-secondary)] uppercase">
                        {memory.type}
                      </span>
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{memory.title}</h3>
                  <p className="text-sm text-[var(--text-secondary)] mb-4 line-clamp-3">
                    {memory.content}
                  </p>
                  {memory.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {memory.tags.map((tag) => (
                        <span key={tag} className="text-xs px-2 py-1 bg-[var(--bg-surface)] text-[var(--text-secondary)] rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="flex gap-2 mt-auto">
                    <Button onClick={() => handleEdit(memory)} variant="secondary" size="sm">
                      Edit
                    </Button>
                    <Button onClick={() => handleDelete(memory.id)} variant="secondary" size="sm">
                      Delete
                    </Button>
                  </div>
                </div>
              </BorderBeam>
            );
          })}
        </div>
      )}

      {/* Memory Form Modal */}
      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title={editingMemory ? 'Edit Memory' : 'Add Memory'}>
        <MemoryForm
          memory={editingMemory}
          onSubmit={handleSubmit}
          onCancel={() => setShowForm(false)}
          loading={submitting}
        />
      </Modal>
    </div>
  );
}

function MemoryForm({ memory, onSubmit, onCancel, loading }) {
  const [formData, setFormData] = useState({
    type: memory?.type || 'note',
    title: memory?.title || '',
    content: memory?.content || '',
    tags: memory?.tags?.join(', ') || '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      tags: formData.tags.split(',').map(t => t.trim()).filter(t => t),
    });
  };

  const memoryTypeOptions = [
    { value: 'character', label: 'Character' },
    { value: 'story', label: 'Story' },
    { value: 'relationship', label: 'Relationship' },
    { value: 'design_decision', label: 'Design Decision' },
    { value: 'art_style', label: 'Art Style' },
    { value: 'preference', label: 'Preference' },
    { value: 'panel', label: 'Panel' },
    { value: 'generated_reference', label: 'Generated Reference' },
    { value: 'character_reference', label: 'Character Reference' },
    { value: 'other_asset', label: 'Other Asset' },
    { value: 'location', label: 'Location' },
    { value: 'note', label: 'Note' },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">Type</label>
        <select
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value })}
          className="w-full px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
        >
          {memoryTypeOptions.map((option) => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">Content</label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData({ ...formData, content: e.target.value })}
          rows={4}
          className="w-full px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">Tags (comma-separated)</label>
        <input
          type="text"
          value={formData.tags}
          onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
          placeholder="e.g., protagonist, sports, high-school"
          className="w-full px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
        />
      </div>

      <div className="flex gap-3 justify-end pt-4">
        <Button onClick={onCancel} variant="secondary">
          Cancel
        </Button>
        <MetalFx preset="chromatic" strength={0.8}>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : memory ? 'Update' : 'Create'}
          </Button>
        </MetalFx>
      </div>
    </form>
  );
}

export default Memory;
