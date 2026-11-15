import { useTheme } from '../../context/ThemeContext';
import { Sun, Moon, Menu } from 'lucide-react';

function Header({ onMenuToggle }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-[var(--bg-surface)] border-b border-[var(--border)]">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onMenuToggle}
              className="lg:hidden text-[var(--text-primary)]"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">MangaCraft</h1>
              <p className="text-sm text-[var(--text-secondary)] hidden sm:block">AI-Powered Manga Creation Workspace</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={toggleTheme}
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition"
              title="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
