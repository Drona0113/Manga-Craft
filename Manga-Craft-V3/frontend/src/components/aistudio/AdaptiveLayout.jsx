import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles } from 'lucide-react';
import CollapsiblePanel from '../common/CollapsiblePanel';
import ConversationSidebar from './ConversationSidebar';
import ProjectIntelligencePanel from './ProjectIntelligencePanel';
import ChatWorkspace from './ChatWorkspace';
import { getProject } from '../../services/projectService';

function AdaptiveLayout({ projectId, conversationId }) {
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  
  // Panel state
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  
  // Screen category for responsive behavior
  const [screenCategory, setScreenCategory] = useState('desktop');
  const [width, setWidth] = useState(window.innerWidth);

  // Load project details
  useEffect(() => {
    if (projectId) {
      loadProject();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const data = await getProject(projectId);
      setProject(data);
    } catch (err) {
      console.error('Failed to load project:', err);
    }
  };

  // Detect screen size
  useEffect(() => {
    const handleResize = () => {
      const newWidth = window.innerWidth;
      setWidth(newWidth);
      
      let newCategory;
      if (newWidth >= 1280) {
        newCategory = 'desktop';
      } else if (newWidth >= 768) {
        newCategory = 'tablet';
      } else {
        newCategory = 'mobile';
      }
      
      setScreenCategory(newCategory);
      
      // Reset panel state based on screen category
      const prefs = loadPanelPreferences(newCategory);
      setLeftPanelOpen(prefs.leftPanelOpen);
      setRightPanelOpen(prefs.rightPanelOpen);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Load panel preferences for screen category
  const loadPanelPreferences = (category) => {
    const defaultPrefs = {
      desktop: { leftPanelOpen: true, rightPanelOpen: true },
      tablet: { leftPanelOpen: false, rightPanelOpen: false },
      mobile: { leftPanelOpen: false, rightPanelOpen: false }
    };
    
    const saved = localStorage.getItem('panelPreferences');
    if (saved) {
      const allPrefs = JSON.parse(saved);
      return allPrefs[category] || defaultPrefs[category];
    }
    return defaultPrefs[category];
  };

  // Save panel preferences for current screen category
  const savePanelPreferences = () => {
    const saved = localStorage.getItem('panelPreferences') || '{}';
    const allPrefs = JSON.parse(saved);
    allPrefs[screenCategory] = {
      leftPanelOpen,
      rightPanelOpen
    };
    localStorage.setItem('panelPreferences', JSON.stringify(allPrefs));
  };

  // Save preferences when panel state changes
  useEffect(() => {
    savePanelPreferences();
  }, [leftPanelOpen, rightPanelOpen, screenCategory]);

  return (
    <div className="flex flex-col h-screen bg-[var(--bg-primary)]">
      {/* Top Header - Full Width */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)] bg-[var(--bg-surface)] shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/projects')}
            className="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors group"
          >
            <ArrowLeft className="w-5 h-5 text-[var(--text-secondary)] group-hover:text-[var(--text-primary)] transition-colors" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent)]/80 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-[var(--text-primary)]">AI Studio</h1>
              <p className="text-xs text-[var(--text-secondary)]">
                Project: {project?.name || 'Loading...'}
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={() => navigate('/projects')}
          className="px-5 py-2.5 bg-[var(--bg-card)] text-[var(--text-primary)] rounded-xl hover:bg-[var(--border)] border border-[var(--border)] hover:border-[var(--accent)] transition-all duration-200 font-medium"
        >
          Back to Projects
        </button>
      </div>

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Conversation Sidebar */}
        {leftPanelOpen ? (
          <CollapsiblePanel
            isOpen={leftPanelOpen}
            onToggle={() => setLeftPanelOpen(!leftPanelOpen)}
            side="left"
            defaultWidth={280}
            minWidth={200}
            maxWidth={350}
          >
            <ConversationSidebar
              projectId={projectId}
              onConversationSelect={(id) => navigate(`/projects/${projectId}/conversation/${id}`)}
              activeConversationId={conversationId}
            />
          </CollapsiblePanel>
        ) : (
          <button
            onClick={() => setLeftPanelOpen(true)}
            className="fixed left-0 top-1/2 -translate-y-1/2 z-20 p-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-r-lg hover:bg-[var(--bg-card)] transition-colors shadow-sm"
            style={{ left: 0 }}
          >
            <svg className="w-4 h-4 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}

        {/* Center Panel - Chat Workspace */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Conversation Header */}
          <div className="flex items-center justify-between px-6 py-3 border-b border-[var(--border)] bg-[var(--bg-surface)]">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              {conversationId ? 'Conversation' : 'Select a conversation'}
            </h2>
          </div>

          {/* Chat Workspace */}
          <div className="flex-1 overflow-hidden">
            <ChatWorkspace
              projectId={projectId}
              conversationId={conversationId}
            />
          </div>
        </div>

        {/* Right Panel - Project Intelligence */}
        {rightPanelOpen ? (
          <CollapsiblePanel
            isOpen={rightPanelOpen}
            onToggle={() => setRightPanelOpen(!rightPanelOpen)}
            side="right"
            defaultWidth={320}
            minWidth={250}
            maxWidth={400}
          >
            <ProjectIntelligencePanel projectId={projectId} />
          </CollapsiblePanel>
        ) : (
          <button
            onClick={() => setRightPanelOpen(true)}
            className="fixed right-0 top-1/2 -translate-y-1/2 z-20 p-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-l-lg hover:bg-[var(--bg-card)] transition-colors shadow-sm"
            style={{ right: 0 }}
          >
            <svg className="w-4 h-4 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

export default AdaptiveLayout;
