import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { conversationService } from '../../services/conversationService';
import { Plus, Search, MoreVertical, Trash2, MessageSquare, Clock } from 'lucide-react';

function ConversationSidebar({ projectId, onConversationSelect, activeConversationId }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    loadConversations();
  }, [projectId]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await conversationService.listConversations(projectId);
      setConversations(data);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    const title = prompt('Enter conversation name:');
    if (!title || !title.trim()) return;
    
    try {
      const newConv = await conversationService.createConversation(projectId, title.trim());
      await loadConversations();
      onConversationSelect(newConv.id);
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
  };

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    if (!confirm('Delete this conversation?')) return;
    
    try {
      await conversationService.deleteConversation(conversationId);
      await loadConversations();
      if (activeConversationId === conversationId) {
        onConversationSelect(null);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="flex flex-col h-full bg-[var(--bg-surface)]">
      {/* Header */}
      <div className="px-3 py-2.5 border-b border-[var(--border)]">
        <h3 className="text-xs font-semibold text-[var(--text-primary)]">Conversations</h3>
      </div>

      {/* New Conversation */}
      <div className="p-3 border-b border-[var(--border)]">
        <button
          onClick={handleCreateConversation}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-[var(--accent)] text-white rounded-lg hover:bg-[var(--accent)]/80 transition-colors text-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New</span>
        </button>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-[var(--border)]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-secondary)]" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-[var(--bg-primary)] border border-[var(--border)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/10 transition-all"
          />
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-6 text-center">
            <div className="w-8 h-8 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-sm text-[var(--text-secondary)]">Loading conversations...</p>
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="p-6 text-center">
            <MessageSquare className="w-12 h-12 text-[var(--text-secondary)] mx-auto mb-3 opacity-50" />
            <p className="text-sm text-[var(--text-secondary)] mb-1">
              {searchQuery ? 'No conversations found' : 'No conversations yet'}
            </p>
            {!searchQuery && (
              <p className="text-xs text-[var(--text-secondary)] opacity-60">
                Click "New Conversation" to start
              </p>
            )}
          </div>
        ) : (
          <div className="p-3 space-y-2">
            {filteredConversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => onConversationSelect(conv.id)}
                className={`group relative p-4 rounded-xl cursor-pointer transition-all duration-200 ${
                  activeConversationId === conv.id
                    ? 'bg-gradient-to-r from-[var(--accent)] to-[var(--accent)]/90 text-white shadow-lg shadow-[var(--accent)]/20'
                    : 'bg-[var(--bg-card)] hover:bg-[var(--bg-primary)] border border-[var(--border)] hover:border-[var(--accent)]/30'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium truncate mb-1 ${
                      activeConversationId === conv.id ? 'text-white' : 'text-[var(--text-primary)]'
                    }`}>
                      {conv.title}
                    </p>
                    <div className={`flex items-center gap-1.5 text-xs ${
                      activeConversationId === conv.id ? 'text-white/70' : 'text-[var(--text-secondary)]'
                    }`}>
                      <Clock className="w-3 h-3" />
                      <span>{formatDate(conv.updated_at)}</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    className={`opacity-0 group-hover:opacity-100 p-1.5 rounded-lg transition-all ${
                      activeConversationId === conv.id
                        ? 'hover:bg-white/20'
                        : 'hover:bg-red-500/10'
                    }`}
                  >
                    <Trash2 className={`w-4 h-4 ${
                      activeConversationId === conv.id ? 'text-white' : 'text-red-400'
                    }`} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ConversationSidebar;
