function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} group`}>
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 ${
          isUser
            ? 'bg-[var(--accent)] text-white'
            : 'bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border)]'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
        <p className={`text-xs mt-2 opacity-60 ${
          isUser ? 'text-white/60' : 'text-[var(--text-secondary)]'
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
