import { useState, useEffect, useRef } from 'react';
import { conversationService } from '../../services/conversationService';
import MessageBubble from './MessageBubble';
import Loading from '../common/Loading';
import { MessageSquare } from 'lucide-react';

function MessageList({ conversationId, refreshKey, streamingContent = '', isStreaming = false }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);
  const messagesEndRef = useRef(null);

  // Auto-scroll as messages arrive AND as the streaming reply grows
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent, isStreaming]);

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

  const getLocalDateKey = (dateString) => {
    const date = new Date(dateString);
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  };

  const formatDateHeading = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    if (getLocalDateKey(dateString) === getLocalDateKey(today.toISOString())) return 'Today';
    if (getLocalDateKey(dateString) === getLocalDateKey(yesterday.toISOString())) return 'Yesterday';

    return date.toLocaleDateString(undefined, {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
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

  if (messages.length === 0 && !streamingContent && !isStreaming) {
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
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => {
          const isFirstMessageOfDay = index === 0 ||
            getLocalDateKey(message.created_at) !== getLocalDateKey(messages[index - 1].created_at);

          return (
            <div key={message.id}>
              {isFirstMessageOfDay && (
                <div className="flex justify-center py-3">
                  <span className="px-3 py-1 text-xs text-[var(--text-secondary)] bg-[var(--bg-card)] rounded-full">
                    {formatDateHeading(message.created_at)}
                  </span>
                </div>
              )}
              <MessageBubble message={message} />
            </div>
          );
        })}
        {isStreaming && !streamingContent && (
          <div className="flex justify-start">
            <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-[var(--text-secondary)] animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-[var(--text-secondary)] animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-[var(--text-secondary)] animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        {streamingContent && (
          <MessageBubble
            message={{
              id: 'streaming',
              role: 'assistant',
              content: streamingContent,
              created_at: new Date().toISOString(),
            }}
            isStreaming={isStreaming}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="flex justify-center p-3 border-t border-[var(--border)]">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="px-4 py-1.5 text-sm bg-[var(--bg-card)] text-[var(--text-primary)] rounded-lg hover:bg-[var(--bg-surface)] border border-[var(--border)] transition-colors disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Load older'}
          </button>
        </div>
      )}
    </div>
  );
}

export default MessageList;
