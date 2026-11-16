import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

function CollapsiblePanel({ 
  isOpen, 
  onToggle, 
  children, 
  side = 'left',
  defaultWidth = 280,
  minWidth = 200,
  maxWidth = 350
}) {
  const [isResizing, setIsResizing] = useState(false);
  const [width, setWidth] = useState(defaultWidth);

  const handleMouseDown = (e) => {
    setIsResizing(true);
    e.preventDefault();
  };

  const handleMouseMove = (e) => {
    if (!isResizing) return;
    
    if (side === 'left') {
      const newWidth = e.clientX;
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setWidth(newWidth);
      }
    } else {
      const newWidth = window.innerWidth - e.clientX;
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setWidth(newWidth);
      }
    }
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  // Add global mouse events for resizing only when isResizing
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing]);

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className={`fixed ${side === 'left' ? 'left-0' : 'right-0'} top-1/2 -translate-y-1/2 z-20 p-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-r-lg hover:bg-[var(--bg-card)] transition-colors`}
        style={{ [side]: 0 }}
      >
        {side === 'left' ? <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronLeft className="w-4 h-4 text-[var(--text-secondary)]" />}
      </button>
    );
  }

  return (
    <div
      className={`h-full flex flex-col bg-[var(--bg-surface)] border-r border-[var(--border)] ${side === 'right' ? 'border-r-0 border-l' : ''}`}
      style={{ width: `${width}px` }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
        <h3 className="text-sm font-medium text-[var(--text-primary)]">Panel</h3>
        <button
          onClick={onToggle}
          className="p-1 hover:bg-[var(--bg-card)] rounded transition-colors"
        >
          {side === 'left' ? <ChevronLeft className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {children}
      </div>

      {/* Resize Handle */}
      <div
        className={`absolute top-0 bottom-0 w-1 cursor-col-resize hover:bg-[var(--accent)] transition-colors ${side === 'left' ? 'right-0' : 'left-0'}`}
        onMouseDown={handleMouseDown}
        style={{ zIndex: 10 }}
      />
    </div>
  );
}

export default CollapsiblePanel;
