import { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, BookOpen, Users, FileText, Database, Sparkles } from 'lucide-react';
import { memoryService } from '../../services/memoryService';

// Compact section component
function IntelligenceSection({ id, title, icon: Icon, isExpanded, onToggle, children, count }) {
  return (
    <div className="border-b border-[var(--border)] last:border-b-0">
      <button
        onClick={() => onToggle(id)}
        className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-[var(--bg-card)] transition-colors group"
      >
        <div className="flex items-center gap-2 flex-1">
          <Icon className={`w-4 h-4 ${
            isExpanded ? 'text-[var(--accent)]' : 'text-[var(--text-secondary)]'
          }`} />
          <span className="text-sm text-[var(--text-primary)]">{title}</span>
          {count !== undefined && count > 0 && (
            <span className="text-xs text-[var(--text-secondary)] bg-[var(--bg-primary)] px-1.5 py-0.5 rounded">{count}</span>
          )}
        </div>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" />
        ) : (
          <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-3 pb-3 pt-1">
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
      count: undefined,
      content: (
        <div className="p-3 bg-[var(--bg-primary)] rounded border border-dashed border-[var(--border)]">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[var(--accent)]" />
            <p className="text-xs text-[var(--text-secondary)]">AI overview in V3.11</p>
          </div>
        </div>
      ),
    },
    {
      id: 'characters',
      title: 'Characters',
      icon: Users,
      count: getMemoriesByType('character').length,
      content: (
        <div className="space-y-2">
          {getMemoriesByType('character').length === 0 ? (
            <p className="text-xs text-[var(--text-secondary)] py-2">No characters</p>
          ) : (
            <>
              {getMemoriesByType('character').slice(0, 3).map((mem) => (
                <div key={mem.id} className="p-2 bg-[var(--bg-primary)] rounded border border-[var(--border)]">
                  <p className="text-xs font-medium text-[var(--text-primary)]">{mem.title}</p>
                </div>
              ))}
              {getMemoriesByType('character').length > 3 && (
                <p className="text-xs text-[var(--text-secondary)] text-center py-1">
                  +{getMemoriesByType('character').length - 3} more
                </p>
              )}
            </>
          )}
        </div>
      ),
    },
    {
      id: 'story',
      title: 'Story',
      icon: FileText,
      count: getMemoriesByType('story').length,
      content: (
        <div className="space-y-2">
          {getMemoriesByType('story').length === 0 ? (
            <p className="text-xs text-[var(--text-secondary)] py-2">No story elements</p>
          ) : (
            <>
              {getMemoriesByType('story').slice(0, 3).map((mem) => (
                <div key={mem.id} className="p-2 bg-[var(--bg-primary)] rounded border border-[var(--border)]">
                  <p className="text-xs font-medium text-[var(--text-primary)]">{mem.title}</p>
                </div>
              ))}
              {getMemoriesByType('story').length > 3 && (
                <p className="text-xs text-[var(--text-secondary)] text-center py-1">
                  +{getMemoriesByType('story').length - 3} more
                </p>
              )}
            </>
          )}
        </div>
      ),
    },
    {
      id: 'context',
      title: 'Context',
      icon: Database,
      count: memories.length,
      content: (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between p-1.5 bg-[var(--bg-primary)] rounded">
            <span className="text-xs text-[var(--text-secondary)]">Characters</span>
            <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('character').length}</span>
          </div>
          <div className="flex items-center justify-between p-1.5 bg-[var(--bg-primary)] rounded">
            <span className="text-xs text-[var(--text-secondary)]">Story</span>
            <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('story').length}</span>
          </div>
          <div className="flex items-center justify-between p-1.5 bg-[var(--bg-primary)] rounded">
            <span className="text-xs text-[var(--text-secondary)]">Relationships</span>
            <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('relationship').length}</span>
          </div>
          <div className="flex items-center justify-between p-1.5 bg-[var(--bg-primary)] rounded">
            <span className="text-xs text-[var(--text-secondary)]">Design</span>
            <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('design_decision').length}</span>
          </div>
          <div className="flex items-center justify-between p-1.5 bg-[var(--bg-primary)] rounded">
            <span className="text-xs text-[var(--text-secondary)]">Art Style</span>
            <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('art_style').length}</span>
          </div>
          <div className="flex items-center justify-between p-1.5 bg-[var(--bg-primary)] rounded">
            <span className="text-xs text-[var(--text-secondary)]">Locations</span>
            <span className="text-xs font-medium text-[var(--accent)]">{getMemoriesByType('location').length}</span>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="flex flex-col h-full bg-[var(--bg-surface)]">
      {/* Header */}
      <div className="px-3 py-2.5 border-b border-[var(--border)]">
        <h3 className="text-xs font-semibold text-[var(--text-primary)] flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-[var(--accent)]" />
          Project Intelligence
        </h3>
      </div>

      {/* Sections */}
      <div className="flex-1 overflow-y-auto">
        {sections.map((section) => (
          <IntelligenceSection
            key={section.id}
            id={section.id}
            title={section.title}
            icon={section.icon}
            isExpanded={expandedSections[section.id]}
            onToggle={toggleSection}
            count={section.count}
          >
            {section.content}
          </IntelligenceSection>
        ))}
      </div>
    </div>
  );
}

export default ProjectIntelligencePanel;
