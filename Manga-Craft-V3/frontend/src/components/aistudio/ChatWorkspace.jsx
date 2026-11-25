import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { conversationService } from '../../services/conversationService';
import { MessageSquare, Sparkles } from 'lucide-react';
import MessageList from './MessageList';
import MessageComposer from './MessageComposer';

function ChatWorkspace({ projectId, conversationId }) {
  const navigate = useNavigate();
  const [conversation, setConversation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [messageRefreshKey, setMessageRefreshKey] = useState(0);

  useEffect(() => {
    if (conversationId) {
      loadConversation();
    } else {
      // No conversation selected - show empty state
      setLoading(false);
    }
  }, [conversationId]);

  const loadConversation = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await conversationService.getConversation(conversationId);
      setConversation(data);
    } catch (err) {
      setError('Failed to load conversation');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (content) => {
    try {
      // Send through the AI endpoint: it saves the user message,
      // generates an AI reply, saves it, and returns both.
      await conversationService.sendChatMessage(conversationId, content);
      // Trigger message list refresh
      setMessageRefreshKey(prev => prev + 1);
    } catch (err) {
      console.error('Failed to send message:', err);
      throw err;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-[var(--accent)] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[var(--text-secondary)]">Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center p-6">
          <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">⚠️</span>
          </div>
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => navigate('/projects')}
            className="px-4 py-2 bg-[var(--bg-card)] text-[var(--text-primary)] rounded-lg hover:bg-[var(--border)] transition-colors"
          >
            Go to Projects
          </button>
        </div>
      </div>
    );
  }

  if (!conversationId) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[var(--accent)]/20 to-[var(--accent)]/5 flex items-center justify-center mb-6">
          <MessageSquare className="w-10 h-10 text-[var(--accent)]" />
        </div>
        <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">No conversation selected</h2>
        <p className="text-[var(--text-secondary)] mb-6 text-center max-w-md">
          Select a conversation from the sidebar to start chatting with your AI assistant
        </p>
        <button
          onClick={() => navigate('/projects')}
          className="px-6 py-3 bg-gradient-to-r from-[var(--accent)] to-[var(--accent)]/80 text-white rounded-xl hover:shadow-lg hover:shadow-[var(--accent)]/20 transition-all duration-200 font-medium"
        >
          Go to Projects
        </button>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center p-6">
          <div className="w-12 h-12 rounded-full bg-[var(--bg-card)] flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">🔍</span>
          </div>
          <p className="text-[var(--text-secondary)]">Conversation not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Message List */}
      <div className="flex-1 overflow-y-auto">
        <MessageList conversationId={conversationId} refreshKey={messageRefreshKey} />
      </div>

      {/* Message Composer */}
      <MessageComposer onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatWorkspace;
