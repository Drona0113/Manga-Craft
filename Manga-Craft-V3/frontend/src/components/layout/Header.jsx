function Header() {
  return (
    <header className="bg-[#2a2a2a] border-b border-[#3a3a3a]">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">MangaCraft</h1>
            <p className="text-sm text-gray-400">AI-Powered Manga Creation Workspace</p>
          </div>
          <nav className="flex gap-4">
            <a href="/projects" className="text-white hover:text-gray-300 transition">Projects</a>
            <a href="/chat" className="text-white hover:text-gray-300 transition">Chat</a>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;
