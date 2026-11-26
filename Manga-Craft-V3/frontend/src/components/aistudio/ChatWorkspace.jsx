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
  const [streamingContent, setStreamingContent] = useState('');
  const [displayedContent, setDisplayedContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isStreamFinal, setIsStreamFinal] = useState(false);

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
    // Reset the streaming buffer for a fresh reply.
    setStreamingContent('');
    setDisplayedContent('');
    setIsStreaming(true);
    setIsStreamFinal(false);

    try {
      await conversationService.streamChatMessage(conversationId, content, {
        // The user message is saved server-side as soon as the stream starts.
        onStart: () => setMessageRefreshKey(prev => prev + 1),
        // Accumulate tokens here; a separate effect reveals them.
        onToken: (token) => setStreamingContent(prev => prev + token),
        onDone: () => setIsStreamFinal(true),
        onError: (message) => {
          setIsStreaming(false);
          setStreamingContent('');
          setDisplayedContent('');
          setError(message);
        },
      });
    } catch (err) {
      console.error('Failed to stream message:', err);
      setIsStreaming(false);
      setStreamingContent('');
      setDisplayedContent('');
      throw err;
    }
  };

  // Reveal the reply a few characters at a time so streaming is visible,
  // even when the whole reply arrives in one fast chunk.
  useEffect(() => {
    if (displayedContent.length >= streamingContent.length) return;
    const timer = setTimeout(() => {
      const remaining = streamingContent.length - displayedContent.length;
      const step = Math.max(2, Math.ceil(remaining / 15));
      setDisplayedContent(streamingContent.slice(0, displayedContent.length + step));
    }, 16);
    return () => clearTimeout(timer);
  }, [streamingContent, displayedContent]);

  // Once the server is done AND the reveal has caught up, clean up and reload
  // so the saved assistant message replaces the temporary streaming bubble.
  useEffect(() => {
    if (!isStreamFinal) return;
    if (displayedContent.length < streamingContent.length) return;
    setIsStreaming(false);
    setIsStreamFinal(false);
    setStreamingContent('');
    setDisplayedContent('');
    setMessageRefreshKey(prev => prev + 1);
  }, [isStreamFinal, displayedContent, streamingContent]);

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
        <MessageList
          conversationId={conversationId}
          refreshKey={messageRefreshKey}
          streamingContent={displayedContent}
          isStreaming={isStreaming}
        />
      </div>

      {/* Message Composer */}
      <MessageComposer onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatWorkspace;
