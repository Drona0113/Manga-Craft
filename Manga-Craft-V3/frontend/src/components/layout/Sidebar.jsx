function Sidebar() {
  return (
    <aside className="w-64 bg-[#2a2a2a] border-r border-[#3a3a3a] min-h-screen">
      <nav className="p-4">
        <ul className="space-y-2">
          <li>
            <a href="/projects" className="block px-4 py-2 text-white hover:bg-[#3a3a3a] rounded-lg transition">
              Projects
            </a>
          </li>
          <li>
            <a href="/chat" className="block px-4 py-2 text-white hover:bg-[#3a3a3a] rounded-lg transition">
              Chat
            </a>
          </li>
          <li>
            <a href="/panels" className="block px-4 py-2 text-white hover:bg-[#3a3a3a] rounded-lg transition">
              Panels
            </a>
          </li>
          <li>
            <a href="/memory" className="block px-4 py-2 text-white hover:bg-[#3a3a3a] rounded-lg transition">
              Memory
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
}

export default Sidebar;
