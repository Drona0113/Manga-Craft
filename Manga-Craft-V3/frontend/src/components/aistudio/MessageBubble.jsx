function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-5 py-3 ${
          isUser
            ? 'bg-gradient-to-br from-[var(--accent)] to-[var(--accent)]/90 text-white shadow-lg shadow-[var(--accent)]/20'
            : 'bg-[var(--bg-card)] text-[var(--text-primary)] border border-[var(--border)] shadow-sm'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
        <p className={`text-xs mt-2 opacity-70 ${
          isUser ? 'text-white/70' : 'text-[var(--text-secondary)]'
        }`}>
          {new Date(message.created_at).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </p>
      </div>
    </div>
  );
}

export default MessageBubble;
