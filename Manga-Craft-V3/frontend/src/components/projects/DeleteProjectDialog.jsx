import Button from '../common/Button';

function DeleteProjectDialog({ project, onConfirm, onCancel, loading }) {
  return (
    <div>
      <p className="text-[var(--text-secondary)] mb-2">
        Are you sure you want to delete this project?
      </p>
      <p className="text-lg font-semibold text-[var(--text-primary)] mb-6">
        {project?.name}
      </p>
      <p className="text-sm text-[var(--text-secondary)] mb-6">
        This action cannot be undone.
      </p>
      <div className="flex gap-3">
        <Button onClick={onConfirm} variant="danger" loading={loading} className="flex-1">
          Delete
        </Button>
        <Button onClick={onCancel} variant="secondary" disabled={loading} className="flex-1">
          Cancel
        </Button>
      </div>
    </div>
  );
}

export default DeleteProjectDialog;
