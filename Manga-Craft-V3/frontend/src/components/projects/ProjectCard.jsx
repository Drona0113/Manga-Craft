function ProjectCard({ project, onEdit, onDelete }) {
  return (
    <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border)] p-6 hover:border-[var(--text-secondary)] transition">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-[var(--text-primary)]">{project.name}</h3>
        <div className="relative">
          <button className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] p-1">
            •••
          </button>
        </div>
      </div>
      {project.description && (
        <p className="text-[var(--text-secondary)] text-sm mb-4 line-clamp-2">{project.description}</p>
      )}
      <div className="text-xs text-[var(--text-secondary)] mb-4">
        {new Date(project.created_at).toLocaleDateString()}
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onEdit(project)}
          className="flex-1 text-sm text-[var(--text-primary)] bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg py-2 hover:bg-[var(--border)] transition"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(project)}
          className="flex-1 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg py-2 hover:bg-red-500/20 transition"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

export default ProjectCard;
