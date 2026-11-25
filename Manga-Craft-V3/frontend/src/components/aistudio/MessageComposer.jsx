import { useState } from 'react';
import { Send, Paperclip, X } from 'lucide-react';

function MessageComposer({ onSendMessage, disabled = false }) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [attachment, setAttachment] = useState(null);
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim() || loading) return;

    setLoading(true);
    try {
      await onSendMessage(content, attachment);
      setContent('');
      setAttachment(null);
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

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAttachment(file);
      setShowAttachmentMenu(false);
    }
  };

  const getAttachmentPreview = () => {
    if (!attachment) return null;
    
    if (attachment.type.startsWith('image/')) {
      return URL.createObjectURL(attachment);
    }
    return null;
  };

  const handleRemoveAttachment = () => {
    setAttachment(null);
  };

  return (
    <div className="p-4 border-t border-[var(--border)] bg-[var(--bg-surface)]">
      {/* Attachment preview */}
      {attachment && (
        <div className="mb-3">
          <div className="inline-flex items-center gap-3 px-3 py-2 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg">
            {attachment.type.startsWith('image/') ? (
              <div className="relative">
                <img
                  src={getAttachmentPreview()}
                  alt={attachment.name}
                  className="w-16 h-16 object-cover rounded"
                />
                <button
                  type="button"
                  onClick={handleRemoveAttachment}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Paperclip className="w-4 h-4 text-[var(--accent)]" />
                <span className="text-sm text-[var(--text-primary)]">{attachment.name}</span>
                <button
                  type="button"
                  onClick={handleRemoveAttachment}
                  className="p-1 text-[var(--text-secondary)] hover:text-red-500 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Input area */}
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={disabled || loading}
            rows={1}
            className="w-full px-4 py-2.5 pr-10 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)] resize-none disabled:opacity-50"
            style={{ minHeight: '42px', maxHeight: '120px' }}
          />
          <button
            type="button"
            onClick={() => setShowAttachmentMenu(!showAttachmentMenu)}
            className="absolute right-2 bottom-2 p-1.5 text-[var(--text-secondary)] hover:text-[var(--accent)] transition-colors"
            title="Attach file"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          {/* Attachment menu */}
          {showAttachmentMenu && (
            <div className="absolute right-0 bottom-full mb-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg shadow-lg p-2 z-10">
              <label className="flex items-center gap-2 px-3 py-2 rounded hover:bg-[var(--bg-card)] cursor-pointer text-sm text-[var(--text-primary)]">
                <input
                  type="file"
                  id="file-input"
                  accept="image/*,.pdf,.doc,.docx"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <Paperclip className="w-4 h-4" />
                Upload file
              </label>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={!content.trim() || loading}
          className="p-2.5 bg-[var(--accent)] text-white rounded-lg hover:bg-[var(--accent)]/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}

export default MessageComposer;
