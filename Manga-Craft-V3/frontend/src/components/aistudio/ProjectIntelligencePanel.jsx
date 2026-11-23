import { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, BookOpen, Users, FileText, Database, Sparkles, MoreHorizontal, Heart, Palette, Settings, Brain } from 'lucide-react';
import { memoryService } from '../../services/memoryService';

// Section component for extensibility
function IntelligenceSection({ id, title, icon: Icon, isExpanded, onToggle, children, actions }) {
  return (
    <div className="border-b border-[var(--border)] last:border-b-0">
      <button
        onClick={() => onToggle(id)}
        className="w-full flex items-center justify-between p-4 hover:bg-[var(--bg-card)] transition-colors group"
      >
        <div className="flex items-center gap-3 flex-1">
          <div className={`p-2 rounded-lg transition-colors ${
            isExpanded ? 'bg-[var(--accent)]/10' : 'bg-[var(--bg-primary)] group-hover:bg-[var(--bg-card)]'
          }`}>
            <Icon className={`w-4 h-4 ${
              isExpanded ? 'text-[var(--accent)]' : 'text-[var(--text-secondary)]'
            }`} />
          </div>
          <span className="text-sm font-medium text-[var(--text-primary)]">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {actions && <div className="opacity-0 group-hover:opacity-100 transition-opacity">{actions}</div>}
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" />
          ) : (
            <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />
          )}
        </div>
      </button>
      
      {isExpanded && (
        <div className="p-4 pt-0">
          {children}
        </div>
      )}
    </div>
  );
}

function ProjectIntelligencePanel({ projectId }) {
  const [expandedSections, setExpandedSections] = useState({
    overview: true,
    characters: false,
    story: false,
    context: false,
  });

  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadMemories();
    }
  }, [projectId]);

  const loadMemories = async () => {
    try {
      setLoading(true);
      const data = await memoryService.listMemories(projectId);
      setMemories(data.memories);
    } catch (err) {
      console.error('Failed to load memories:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getMemoriesByType = (type) => {
    return memories.filter(m => m.type === type);
  };

  const navigateToMemory = () => {
    window.location.href = '/memory';
  };

  // Sections configuration - easily extensible for future features
  const sections = [
    {
      id: 'overview',
      title: 'Overview',
      icon: BookOpen,
      content: (
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-[var(--bg-primary)] rounded-lg border border-dashed border-[var(--border)]">
            <Sparkles className="w-4 h-4 text-[var(--accent)]" />
            <div className="flex-1">
              <p className="text-sm text-[var(--text-secondary)]">AI-generated project overview</p>
              <p className="text-xs text-[var(--accent)] mt-0.5">Coming in V3.11 (AI Orchestration)</p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'characters',
      title: 'Characters',
      icon: Users,
      content: (
        <div className="space-y-3">
          {loading ? (
            <div className="text-center py-4">
              <p className="text-sm text-[var(--text-secondary)]">Loading...</p>
            </div>
          ) : getMemoriesByType('character').length === 0 ? (
            <div className="flex items-center gap-3 p-3 bg-[var(--bg-primary)] rounded-lg border border-dashed border-[var(--border)]">
              <Users className="w-4 h-4 text-[var(--text-secondary)]" />
              <div className="flex-1">
                <p className="text-sm text-[var(--text-secondary)]">No characters yet.</p>
                <p className="text-xs text-[var(--accent)] mt-0.5">Add in Memory section</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {getMemoriesByType('character').slice(0, 3).map((mem) => (
                <div key={mem.id} className="p-3 bg-[var(--bg-primary)] rounded-lg border border-[var(--border)]">
                  <p className="text-sm font-medium text-[var(--text-primary)]">{mem.title}</p>
                  <p className="text-xs text-[var(--text-secondary)] line-clamp-2 mt-1">{mem.content}</p>
                </div>
              ))}
              {getMemoriesByType('character').length > 3 && (
                <p className="text-xs text-[var(--accent)] text-center py-1">
                  +{getMemoriesByType('character').length - 3} more
                </p>
              )}
              <button
                onClick={navigateToMemory}
                className="w-full text-xs text-[var(--accent)] hover:text-[var(--accent)]/80 text-center py-2"
              >
                View All in Memory →
              </button>
            </div>
          )}
        </div>
      ),
    },
    {
      id: 'story',
      title: 'Story',
      icon: FileText,
      content: (
        <div className="space-y-3">
          {loading ? (
            <div className="text-center py-4">
              <p className="text-sm text-[var(--text-secondary)]">Loading...</p>
            </div>
          ) : getMemoriesByType('story').length === 0 ? (
            <div className="flex items-center gap-3 p-3 bg-[var(--bg-primary)] rounded-lg border border-dashed border-[var(--border)]">
              <FileText className="w-4 h-4 text-[var(--text-secondary)]" />
              <div className="flex-1">
                <p className="text-sm text-[var(--text-secondary)]">No story details yet.</p>
                <p className="text-xs text-[var(--accent)] mt-0.5">Add in Memory section</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {getMemoriesByType('story').slice(0, 3).map((mem) => (
                <div key={mem.id} className="p-3 bg-[var(--bg-primary)] rounded-lg border border-[var(--border)]">
                  <p className="text-sm font-medium text-[var(--text-primary)]">{mem.title}</p>
                  <p className="text-xs text-[var(--text-secondary)] line-clamp-2 mt-1">{mem.content}</p>
                </div>
              ))}
              {getMemoriesByType('story').length > 3 && (
                <p className="text-xs text-[var(--accent)] text-center py-1">
                  +{getMemoriesByType('story').length - 3} more
                </p>
              )}
              <button
                onClick={navigateToMemory}
                className="w-full text-xs text-[var(--accent)] hover:text-[var(--accent)]/80 text-center py-2"
              >
                View All in Memory →
              </button>
            </div>
          )}
        </div>
      ),
    },
    {
      id: 'context',
      title: 'Context',
      icon: Database,
      content: (
        <div className="space-y-3">
          <div className="p-3 bg-[var(--bg-primary)] rounded-lg border border-dashed border-[var(--border)]">
            <p className="text-sm text-[var(--text-secondary)] mb-2">Memory: {memories.length} items</p>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Characters</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('character').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Story</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('story').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Relationships</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('relationship').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Design Decisions</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('design_decision').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Art Style</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('art_style').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Preferences</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('preference').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Panels</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('panel').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Locations</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('location').length}</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Notes</span>
                <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('note').length}</span>
              </div>
            </div>
            <button
              onClick={navigateToMemory}
              className="w-full text-xs text-[var(--accent)] hover:text-[var(--accent)]/80 text-center py-2 mt-3"
            >
              View All in Memory →
            </button>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="flex flex-col h-full bg-[var(--bg-surface)]">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)]">
        <h3 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[var(--accent)]" />
          Project Intelligence
        </h3>
      </div>

      {/* Sections */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {sections.map((section) => (
          <IntelligenceSection
            key={section.id}
            id={section.id}
            title={section.title}
            icon={section.icon}
            isExpanded={expandedSections[section.id]}
            onToggle={toggleSection}
          >
            {section.content}
          </IntelligenceSection>
        ))}
      </div>
    </div>
  );
}

export default ProjectIntelligencePanel;
