import { useState } from 'react';
import { MoreVertical } from 'lucide-react';

function ProjectCard({ project, onEdit, onDelete }) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border)] p-6 hover:border-[var(--text-secondary)] transition">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-[var(--text-primary)]">{project.name}</h3>
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] p-1"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
          {showMenu && (
            <>
              <div className="absolute right-0 top-8 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg shadow-lg z-10 min-w-[120px]">
                <button
                  onClick={() => {
                    onEdit(project);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-card)] transition"
                >
                  Edit
                </button>
                <button
                  onClick={() => {
                    onDelete(project);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 transition"
                >
                  Delete
                </button>
              </div>
              <div
                className="fixed inset-0 z-0"
                onClick={() => setShowMenu(false)}
              />
            </>
          )}
        </div>
      </div>
      {project.description && (
        <p className="text-[var(--text-secondary)] text-sm mb-4 line-clamp-2">{project.description}</p>
      )}
      <div className="text-xs text-[var(--text-secondary)] mb-4">
        {new Date(project.created_at).toLocaleDateString()}
      </div>
    </div>
  );
}

export default ProjectCard;
