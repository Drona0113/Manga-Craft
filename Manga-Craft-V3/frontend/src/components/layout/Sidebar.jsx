import { useLocation, Link } from 'react-router-dom';

function Sidebar({ mobileOpen, onClose }) {
  const location = useLocation();

  const navItems = [
    { section: 'Workspace', items: [
      { path: '/', label: 'Home', active: location.pathname === '/' },
      { path: '/projects', label: 'Projects', active: location.pathname === '/projects' },
    ]},
    { section: 'Library', items: [
      { path: '/memory', label: 'Memory', active: location.pathname === '/memory' },
      { path: '/references', label: 'References', disabled: true },
    ]},
    { section: 'General', items: [
      { path: '/settings', label: 'Settings', disabled: true },
    ]},
  ];

  return (
    <>
      <aside className="w-64 bg-[var(--bg-surface)] border-r border-[var(--border)] min-h-screen hidden lg:block">
        <nav className="p-4">
          {navItems.map((group, groupIndex) => (
            <div key={groupIndex} className="mb-6">
              <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3">
                {group.section}
              </h3>
              <ul className="space-y-1">
                {group.items.map((item, itemIndex) => (
                  <li key={itemIndex}>
                    {item.disabled ? (
                      <span className="block px-4 py-2 rounded-lg text-[var(--text-secondary)] opacity-50 cursor-not-allowed">
                        {item.label}
                      </span>
                    ) : (
                      <Link
                        to={item.path}
                        onClick={onClose}
                        className={`block px-4 py-2 rounded-lg transition ${
                          item.active
                            ? 'bg-[var(--accent)] text-white'
                            : 'text-[var(--text-primary)] hover:bg-[var(--bg-card)]'
                        }`}
                      >
                        {item.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
      </aside>
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[var(--bg-surface)] border-r border-[var(--border)] transform transition-transform lg:hidden ${
        mobileOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <nav className="p-4">
          {navItems.map((group, groupIndex) => (
            <div key={groupIndex} className="mb-6">
              <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3">
                {group.section}
              </h3>
              <ul className="space-y-1">
                {group.items.map((item, itemIndex) => (
                  <li key={itemIndex}>
                    {item.disabled ? (
                      <span className="block px-4 py-2 rounded-lg text-[var(--text-secondary)] opacity-50 cursor-not-allowed">
                        {item.label}
                      </span>
                    ) : (
                      <Link
                        to={item.path}
                        onClick={onClose}
                        className={`block px-4 py-2 rounded-lg transition ${
                          item.active
                            ? 'bg-[var(--accent)] text-white'
                            : 'text-[var(--text-primary)] hover:bg-[var(--bg-card)]'
                        }`}
                      >
                        {item.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
      </aside>
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
    </>
  );
}

export default Sidebar;
