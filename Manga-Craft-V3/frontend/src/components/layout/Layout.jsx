import Header from './Header';
import Sidebar from './Sidebar';

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-[#1a1a1a]">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

export default Layout;
