import { useState } from 'react';
import { ChevronDown, ChevronRight, BookOpen, Users, FileText, Database, Sparkles, MoreHorizontal } from 'lucide-react';

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

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
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
              <p className="text-sm text-[var(--text-secondary)]">No project details yet.</p>
              <p className="text-xs text-[var(--accent)] mt-0.5">Details will be added in V3.9</p>
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
          <div className="flex items-center gap-3 p-3 bg-[var(--bg-primary)] rounded-lg border border-dashed border-[var(--border)]">
            <Users className="w-4 h-4 text-[var(--text-secondary)]" />
            <div className="flex-1">
              <p className="text-sm text-[var(--text-secondary)]">No characters yet.</p>
              <p className="text-xs text-[var(--accent)] mt-0.5">Manage characters in the Memory section</p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'story',
      title: 'Story',
      icon: FileText,
      content: (
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-[var(--bg-primary)] rounded-lg border border-dashed border-[var(--border)]">
            <FileText className="w-4 h-4 text-[var(--text-secondary)]" />
            <div className="flex-1">
              <p className="text-sm text-[var(--text-secondary)]">No story details yet.</p>
              <p className="text-xs text-[var(--accent)] mt-0.5">Add story elements in the Memory section</p>
            </div>
          </div>
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
            <p className="text-sm text-[var(--text-secondary)] mb-2">No context available yet.</p>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">References</span>
                <span className="text-xs font-medium text-[var(--accent)]">0 items</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Panels</span>
                <span className="text-xs font-medium text-[var(--accent)]">0 items</span>
              </div>
              <div className="flex items-center justify-between p-1.5 bg-[var(--bg-surface)] rounded">
                <span className="text-xs text-[var(--text-secondary)]">Memory</span>
                <span className="text-xs font-medium text-[var(--accent)]">0 items</span>
              </div>
            </div>
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

      {/* Sections - Custom scrollbar */}
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
