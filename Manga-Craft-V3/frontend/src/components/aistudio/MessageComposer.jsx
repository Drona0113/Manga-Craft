import { useState } from 'react';
import { Send } from 'lucide-react';
import Button from '../common/Button';

function MessageComposer({ onSendMessage, disabled = false }) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim() || loading) return;

    setLoading(true);
    try {
      await onSendMessage(content);
      setContent('');
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message... (Shift+Enter for new line)"
        disabled={disabled || loading}
        rows={3}
        className="w-full px-4 py-3 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)] resize-none disabled:opacity-50"
      />
      <div className="flex justify-end">
        <Button
          type="submit"
          loading={loading}
          disabled={!content.trim() || disabled}
          className="flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
          Send
        </Button>
      </div>
    </form>
  );
}

export default MessageComposer;
