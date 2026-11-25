import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { conversationService } from '../../services/conversationService';
import { getProject } from '../../services/projectService';
import { panelService } from '../../services/panelService';
import { memoryService } from '../../services/memoryService';
import { MessageSquare, Layers, Users, FileText, Image as ImageIcon, Grid, Sparkles, Plus, ArrowLeft, ChevronLeft, ChevronRight, Menu, X } from 'lucide-react';
import ConversationSidebar from './ConversationSidebar';
import ChatWorkspace from './ChatWorkspace';
import ProjectIntelligencePanel from './ProjectIntelligencePanel';

// Workspace tools
const WORKSPACE_TOOLS = [
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'panels', label: 'Panels', icon: ImageIcon },
  { id: 'characters', label: 'Characters', icon: Users },
  { id: 'story', label: 'Story', icon: FileText },
  { id: 'references', label: 'References', icon: Layers },
];

function AdaptiveLayout() {
  const { projectId, conversationId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [activeTool, setActiveTool] = useState(() => {
    // Restore tool from localStorage
    const saved = localStorage.getItem('activeTool');
    return saved || 'chat';
  });
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [toolsData, setToolsData] = useState({});

  // Save tool to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('activeTool', activeTool);
  }, [activeTool]);

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadToolsData();
    }
  }, [projectId, activeTool]);

  const loadProject = async () => {
    try {
      const data = await getProject(projectId);
      setProject(data);
    } catch (err) {
      console.error('Failed to load project:', err);
    }
  };

  const loadToolsData = async () => {
    try {
      if (activeTool === 'panels') {
        const data = await panelService.listPanels(projectId);
        setToolsData(prev => ({ ...prev, panels: data.panels }));
      } else if (activeTool === 'characters') {
        const data = await memoryService.listMemories(projectId, 'character');
        setToolsData(prev => ({ ...prev, characters: data.memories }));
      } else if (activeTool === 'story') {
        const data = await memoryService.listMemories(projectId, 'story');
        setToolsData(prev => ({ ...prev, story: data.memories }));
      }
    } catch (err) {
      console.error('Failed to load tools data:', err);
    }
  };

  const renderToolArea = () => {
    switch (activeTool) {
      case 'chat':
        return <ChatWorkspace projectId={projectId} conversationId={conversationId} />;
      case 'panels':
        return <PanelsWorkspace panels={toolsData.panels || []} projectId={projectId} />;
      case 'characters':
        return <CharactersWorkspace characters={toolsData.characters || []} projectId={projectId} />;
      case 'story':
        return <StoryWorkspace story={toolsData.story || []} projectId={projectId} />;
      case 'references':
        return <ReferencesWorkspace projectId={projectId} />;
      default:
        return <div className="flex items-center justify-center h-full text-[var(--text-secondary)]">
          Tool coming soon...
        </div>;
    }
  };

  // Workspace-specific components
  function PanelsWorkspace({ panels, projectId }) {
    const [viewMode, setViewMode] = useState('grid'); // grid, storyboard, list
    const [uploading, setUploading] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [dragActive, setDragActive] = useState(false);

    const handleFileSelect = (e) => {
      const files = Array.from(e.target.files);
      const validFiles = files.filter(file => {
        if (file.size > 10 * 1024 * 1024) {
          alert(`${file.name} is too large. Maximum size is 10MB.`);
          return false;
        }
        return true;
      });
      setSelectedFiles(validFiles);
    };

    const handleUpload = async () => {
      if (selectedFiles.length === 0) return;
      try {
        setUploading(true);
        // Upload all selected files
        await Promise.all(selectedFiles.map(file => panelService.uploadPanel(projectId, file)));
        setSelectedFiles([]);
        loadToolsData();
      } catch (err) {
        console.error('Failed to upload panels:', err);
      } finally {
        setUploading(false);
      }
    };

    const handleDelete = async (panelId) => {
      if (!confirm('Delete this panel?')) return;
      try {
        await panelService.deletePanel(panelId);
        loadToolsData();
      } catch (err) {
        console.error('Failed to delete panel:', err);
      }
    };

    const handleSaveNotes = async (panelId, notes) => {
      try {
        await panelService.updatePanel(panelId, { notes });
      } catch (err) {
        console.error('Failed to save panel notes:', err);
      }
    };

    const handleDrag = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === 'dragenter' || e.type === 'dragover') {
        setDragActive(true);
      } else if (e.type === 'dragleave') {
        setDragActive(false);
      }
    };

    const handleDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const files = Array.from(e.dataTransfer.files);
        const validFiles = files.filter(file => {
          if (file.size > 10 * 1024 * 1024) {
            alert(`${file.name} is too large. Maximum size is 10MB.`);
            return false;
          }
          return true;
        });
        setSelectedFiles(validFiles);
      }
    };

    const removeFile = (index) => {
      setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    return (
      <div className="h-full flex flex-col">
        {/* Workspace Toolbar */}
        <div className="h-14 border-b border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            {/* View Mode Selector */}
            <div className="flex items-center bg-[var(--bg-card)] rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1.5 rounded-md text-sm transition-all ${
                  viewMode === 'grid' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-primary)] hover:bg-[var(--border)]'
                }`}
              >
                Grid
              </button>
              <button
                onClick={() => setViewMode('storyboard')}
                className={`px-3 py-1.5 rounded-md text-sm transition-all ${
                  viewMode === 'storyboard' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-primary)] hover:bg-[var(--border)]'
                }`}
              >
                Storyboard
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-1.5 rounded-md text-sm transition-all ${
                  viewMode === 'list' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-primary)] hover:bg-[var(--border)]'
                }`}
              >
                List
              </button>
            </div>

            {/* Selection Info removed - was only used by the now-removed Inspector */}
          </div>

          <div className="flex items-center gap-2">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileSelect}
              multiple
              className="hidden"
              id="panel-upload"
            />
            <label
              htmlFor="panel-upload"
              className="px-4 py-2 bg-[var(--bg-card)] text-[var(--text-primary)] rounded-lg hover:bg-[var(--border)] border border-[var(--border)] cursor-pointer flex items-center gap-2 text-sm"
            >
              <Plus className="w-4 h-4" />
              Upload
            </label>
            {selectedFiles.length > 0 && (
              <>
                <span className="text-sm text-[var(--text-secondary)]">{selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''}</span>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:bg-[var(--accent)]/80 transition-colors text-sm"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </>
            )}
          </div>
        </div>

        {/* File Preview */}
        {selectedFiles.length > 0 && (
          <div className="px-4 py-2 border-b border-[var(--border)] bg-[var(--bg-surface)]">
            <div className="flex gap-2 overflow-x-auto">
              {selectedFiles.map((file, index) => (
                <div key={index} className="relative flex-shrink-0">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={file.name}
                    className="w-16 h-16 object-cover rounded border border-[var(--border)]"
                  />
                  <button
                    onClick={() => removeFile(index)}
                    className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                  >
                    <Plus className="w-3 h-3 rotate-45" />
                  </button>
                  <p className="text-xs text-[var(--text-secondary)] mt-1 truncate w-16">{file.name}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main Workspace Area */}
        <div className="flex-1 p-4 overflow-auto">
          {panels.length === 0 ? (
              <div
                className={`h-full border-2 border-dashed rounded-lg flex flex-col items-center justify-center transition-colors ${
                  dragActive ? 'border-[var(--accent)] bg-[var(--accent)]/5' : 'border-[var(--border)]'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <ImageIcon className="w-16 h-16 text-[var(--text-secondary)] mb-4 opacity-50" />
                <p className="text-[var(--text-secondary)] text-lg mb-2">No panels yet</p>
                <p className="text-sm text-[var(--text-secondary)]">Drag & drop images or click Upload to get started</p>
              </div>
            ) : viewMode === 'grid' ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {panels.map((panel, index) => (
                  <div
                    key={panel.id}
                    className="relative group aspect-square bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg overflow-hidden hover:border-[var(--accent)] transition-all"
                  >
                    <img
                      src={`http://localhost:8000/${panel.file_path}`}
                      alt={panel.file_name}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="absolute bottom-0 left-0 right-0 p-3">
                        <p className="text-white text-sm truncate">{panel.file_name}</p>
                        <p className="text-white/70 text-xs">{formatFileSize(panel.file_size)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(panel.id)}
                      className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Plus className="w-4 h-4 rotate-45" />
                </button>
                  </div>
                ))}
              </div>
            ) : viewMode === 'storyboard' ? (
              <div className="space-y-4">
                {panels.map((panel, index) => (
                  <div
                    key={panel.id}
                    className="flex items-start gap-4 p-4 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg hover:border-[var(--accent)] transition-all"
                  >
                    <div className="flex-shrink-0 w-8 h-8 bg-[var(--accent)] text-white rounded-lg flex items-center justify-center font-semibold">
                      {index + 1}
                    </div>
                    <div className="flex-1 h-24 bg-[var(--bg-card)] rounded-lg overflow-hidden">
                      <img
                        src={`http://localhost:8000/${panel.file_path}`}
                        alt={panel.file_name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-[var(--text-primary)] mb-1">{panel.file_name}</p>
                      <p className="text-sm text-[var(--text-secondary)] mb-2">{formatFileSize(panel.file_size)}</p>
                      <textarea
                        placeholder="Scene notes..."
                        defaultValue={panel.notes || ''}
                        onBlur={(e) => handleSaveNotes(panel.id, e.target.value)}
                        className="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-sm text-[var(--text-primary)] resize-none"
                        rows={2}
                      />
                    </div>
                    <button
                      onClick={() => handleDelete(panel.id)}
                      className="p-2 text-[var(--text-secondary)] hover:text-red-500 transition-colors"
                    >
                      <Plus className="w-4 h-4 rotate-45" />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[var(--bg-card)]">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-[var(--text-primary)]">Name</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-[var(--text-primary)]">Size</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-[var(--text-primary)]">Type</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-[var(--text-primary)]">Date</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-[var(--text-primary)]">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {panels.map((panel) => (
                      <tr key={panel.id} className="border-t border-[var(--border)] hover:bg-[var(--bg-card)]">
                        <td className="px-4 py-3 text-sm text-[var(--text-primary)]">{panel.file_name}</td>
                        <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{formatFileSize(panel.file_size)}</td>
                        <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{panel.file_type}</td>
                        <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{new Date(panel.created_at).toLocaleDateString()}</td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => handleDelete(panel.id)}
                            className="p-1 text-[var(--text-secondary)] hover:text-red-500 transition-colors"
                          >
                            <Plus className="w-4 h-4 rotate-45" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
    );
  }

  function CharactersWorkspace({ characters, projectId }) {
    const [showAddModal, setShowAddModal] = useState(false);
    const [newCharacter, setNewCharacter] = useState({ title: '', content: '', tags: '' });

    const handleAdd = async () => {
      if (!newCharacter.title || !newCharacter.content) return;
      try {
        await memoryService.createMemory(projectId, {
          type: 'character',
          title: newCharacter.title,
          content: newCharacter.content,
          tags: newCharacter.tags.split(',').map(t => t.trim()).filter(t => t)
        });
        setNewCharacter({ title: '', content: '', tags: '' });
        setShowAddModal(false);
        loadToolsData();
      } catch (err) {
        console.error('Failed to add character:', err);
      }
    };

    const handleDelete = async (id) => {
      if (!confirm('Delete this character?')) return;
      try {
        await memoryService.deleteMemory(id);
        loadToolsData();
      } catch (err) {
        console.error('Failed to delete character:', err);
      }
    };

    return (
      <div className="h-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">Characters</h2>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:bg-[var(--accent)]/80 transition-colors flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Character
          </button>
        </div>
        {showAddModal && (
          <div className="mb-6 p-4 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg">
            <input
              type="text"
              placeholder="Character name"
              value={newCharacter.title}
              onChange={(e) => setNewCharacter({ ...newCharacter, title: e.target.value })}
              className="w-full px-3 py-2 mb-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
            />
            <textarea
              placeholder="Character description"
              value={newCharacter.content}
              onChange={(e) => setNewCharacter({ ...newCharacter, content: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 mb-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
            />
            <input
              type="text"
              placeholder="Tags (comma-separated)"
              value={newCharacter.tags}
              onChange={(e) => setNewCharacter({ ...newCharacter, tags: e.target.value })}
              className="w-full px-3 py-2 mb-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
            />
            <div className="flex gap-2">
              <button onClick={handleAdd} className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg">Add</button>
              <button onClick={() => setShowAddModal(false)} className="px-4 py-2 bg-[var(--bg-card)] text-[var(--text-primary)] rounded-lg">Cancel</button>
            </div>
          </div>
        )}
        {characters.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-[var(--border)] rounded-lg">
            <Users className="w-12 h-12 text-[var(--text-secondary)] mb-4 opacity-50" />
            <p className="text-[var(--text-secondary)]">No characters yet</p>
            <p className="text-sm text-[var(--text-secondary)] mt-1">Add your first character</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {characters.map((char) => (
              <div key={char.id} className="p-4 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg hover:border-[var(--accent)] transition-colors relative group">
                <button
                  onClick={() => handleDelete(char.id)}
                  className="absolute top-2 right-2 p-1 text-[var(--text-secondary)] hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Plus className="w-4 h-4 rotate-45" />
                </button>
                <h3 className="font-semibold text-[var(--text-primary)] mb-2">{char.title}</h3>
                <p className="text-sm text-[var(--text-secondary)] line-clamp-3">{char.content}</p>
                {char.tags && char.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {char.tags.map((tag, i) => (
                      <span key={i} className="text-xs px-2 py-1 bg-[var(--bg-card)] text-[var(--text-secondary)] rounded">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  function StoryWorkspace({ story, projectId }) {
    const [showAddModal, setShowAddModal] = useState(false);
    const [newStory, setNewStory] = useState({ title: '', content: '', tags: '' });

    const handleAdd = async () => {
      if (!newStory.title || !newStory.content) return;
      try {
        await memoryService.createMemory(projectId, {
          type: 'story',
          title: newStory.title,
          content: newStory.content,
          tags: newStory.tags.split(',').map(t => t.trim()).filter(t => t)
        });
        setNewStory({ title: '', content: '', tags: '' });
        setShowAddModal(false);
        loadToolsData();
      } catch (err) {
        console.error('Failed to add story:', err);
      }
    };

    const handleDelete = async (id) => {
      if (!confirm('Delete this story element?')) return;
      try {
        await memoryService.deleteMemory(id);
        loadToolsData();
      } catch (err) {
        console.error('Failed to delete story:', err);
      }
    };

    return (
      <div className="h-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">Story</h2>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:bg-[var(--accent)]/80 transition-colors flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Story Element
          </button>
        </div>
        {showAddModal && (
          <div className="mb-6 p-4 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg">
            <input
              type="text"
              placeholder="Story element title"
              value={newStory.title}
              onChange={(e) => setNewStory({ ...newStory, title: e.target.value })}
              className="w-full px-3 py-2 mb-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
            />
            <textarea
              placeholder="Story content"
              value={newStory.content}
              onChange={(e) => setNewStory({ ...newStory, content: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 mb-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
            />
            <input
              type="text"
              placeholder="Tags (comma-separated)"
              value={newStory.tags}
              onChange={(e) => setNewStory({ ...newStory, tags: e.target.value })}
              className="w-full px-3 py-2 mb-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
            />
            <div className="flex gap-2">
              <button onClick={handleAdd} className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg">Add</button>
              <button onClick={() => setShowAddModal(false)} className="px-4 py-2 bg-[var(--bg-card)] text-[var(--text-primary)] rounded-lg">Cancel</button>
            </div>
          </div>
        )}
        {story.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-[var(--border)] rounded-lg">
            <FileText className="w-12 h-12 text-[var(--text-secondary)] mb-4 opacity-50" />
            <p className="text-[var(--text-secondary)]">No story elements yet</p>
            <p className="text-sm text-[var(--text-secondary)] mt-1">Add your first story element</p>
          </div>
        ) : (
          <div className="space-y-4">
            {story.map((item) => (
              <div key={item.id} className="p-4 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg relative group">
                <button
                  onClick={() => handleDelete(item.id)}
                  className="absolute top-2 right-2 p-1 text-[var(--text-secondary)] hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Plus className="w-4 h-4 rotate-45" />
                </button>
                <h3 className="font-semibold text-[var(--text-primary)] mb-2">{item.title}</h3>
                <p className="text-sm text-[var(--text-secondary)]">{item.content}</p>
                {item.tags && item.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {item.tags.map((tag, i) => (
                      <span key={i} className="text-xs px-2 py-1 bg-[var(--bg-card)] text-[var(--text-secondary)] rounded">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  function ReferencesWorkspace({ projectId }) {
    return (
      <div className="h-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">References</h2>
          <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:bg-[var(--accent)]/80 transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Generate Reference
          </button>
        </div>
        <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-[var(--border)] rounded-lg">
          <Layers className="w-12 h-12 text-[var(--text-secondary)] mb-4 opacity-50" />
          <p className="text-[var(--text-secondary)]">No references yet</p>
          <p className="text-sm text-[var(--text-secondary)] mt-1">Generate references from panels (V3.15)</p>
        </div>
      </div>
    );
  }

  if (!projectId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-[var(--text-secondary)]">Loading project...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-[var(--bg-primary)]">
      {/* Top Bar - Project Header + Tools */}
      <div className="h-14 border-b border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/projects')}
            className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors flex items-center gap-2 text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Projects
          </button>
          <div className="h-6 w-px bg-[var(--border)]"></div>
          <div>
            <h1 className="text-base font-semibold text-[var(--text-primary)]">{project?.name || 'Loading...'}</h1>
          </div>
        </div>

        {/* Tools Selector */}
        <div className="flex items-center gap-1">
          {WORKSPACE_TOOLS.map((tool) => (
            <button
              key={tool.id}
              onClick={() => setActiveTool(tool.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-md transition-all text-sm ${
                activeTool === tool.id
                  ? 'bg-[var(--accent)] text-white'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card)]'
              }`}
            >
              <tool.icon className="w-4 h-4" />
              {tool.label}
            </button>
          ))}
        </div>

        {/* Panel Toggles */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setLeftPanelOpen(!leftPanelOpen)}
            className={`p-2 rounded-md transition-all ${
              leftPanelOpen ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
            title="Toggle conversations"
          >
            <Menu className="w-4 h-4" />
          </button>
          <button
            onClick={() => setRightPanelOpen(!rightPanelOpen)}
            className={`p-2 rounded-md transition-all ${
              rightPanelOpen ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
            title="Toggle project intelligence"
          >
            <Grid className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Workspace Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Conversations (only visible in Chat tool) */}
        {activeTool === 'chat' && leftPanelOpen && (
          <div className="w-72 border-r border-[var(--border)] flex flex-col bg-[var(--bg-surface)] flex-shrink-0">
            <ConversationSidebar 
              projectId={projectId} 
              conversationId={conversationId}
              onConversationSelect={(id) => navigate(`/projects/${projectId}/conversation/${id}`)}
            />
          </div>
        )}

        {/* Left Panel Toggle Button (when collapsed) */}
        {activeTool === 'chat' && !leftPanelOpen && (
          <button
            onClick={() => setLeftPanelOpen(true)}
            className="w-8 border-r border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors flex-shrink-0"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        )}

        {/* Center - Tool Workspace */}
        <div className="flex-1 flex flex-col min-w-0 bg-[var(--bg-primary)] overflow-hidden">
          {renderToolArea()}
        </div>

        {/* Right Panel - Project Intelligence */}
        {rightPanelOpen && (
          <div className="w-80 border-l border-[var(--border)] flex flex-col bg-[var(--bg-surface)] flex-shrink-0">
            <ProjectIntelligencePanel projectId={projectId} />
          </div>
        )}

        {/* Right Panel Toggle Button (when collapsed) */}
        {!rightPanelOpen && (
          <button
            onClick={() => setRightPanelOpen(true)}
            className="w-8 border-l border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors flex-shrink-0"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}

export default AdaptiveLayout;
