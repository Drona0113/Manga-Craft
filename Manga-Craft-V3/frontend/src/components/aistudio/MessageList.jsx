import { useState, useEffect, useRef } from 'react';
import { conversationService } from '../../services/conversationService';
import MessageBubble from './MessageBubble';
import Loading from '../common/Loading';
import { MessageSquare } from 'lucide-react';

function MessageList({ conversationId, refreshKey }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    loadMessages();
  }, [conversationId, refreshKey]);

  const loadMessages = async (skip = 0) => {
    try {
      setLoading(true);
      const response = await conversationService.getMessages(conversationId, skip, 50);
      
      if (skip === 0) {
        // Initial load - already in chronological order (oldest first)
        setMessages(response.messages);
      } else {
        // Load more - prepend older messages
        const existingIds = new Set(messages.map(m => m.id));
        const newMessages = response.messages.filter(m => !existingIds.has(m.id));
        setMessages([...newMessages, ...messages]);
      }
      
      setHasMore(response.has_more);
      setTotal(response.total);
    } catch (err) {
      console.error('Failed to load messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    loadMessages(messages.length);
  };

  if (loading && messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-[var(--accent)] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[var(--text-secondary)]">Loading messages...</p>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--accent)]/20 to-[var(--accent)]/5 flex items-center justify-center mb-4">
          <MessageSquare className="w-8 h-8 text-[var(--accent)]" />
        </div>
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">No messages yet</h3>
        <p className="text-[var(--text-secondary)] text-center max-w-sm">
          Start the conversation by typing a message below
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="flex justify-center p-4">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="px-6 py-2.5 bg-[var(--bg-card)] text-[var(--text-primary)] rounded-xl hover:bg-[var(--bg-surface)] border border-[var(--border)] hover:border-[var(--accent)] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Loading...' : 'Load older messages'}
          </button>
        </div>
      )}
    </div>
  );
}

export default MessageList;
