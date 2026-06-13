import { useState } from 'react';
import AdminDashboard from './AdminDashboard';
import DocumentIngestion from './DocumentIngestion';
import KnowledgeSearch from './KnowledgeSearch';
import InsightsDashboard from './InsightsDashboard';

export default function App() {
  const [currentPage, setCurrentPage] = useState('insights');

  const navItems = [
    { id: 'insights', icon: 'dashboard', label: 'Dashboard' },
    { id: 'admin', icon: 'description', label: 'Documents' },
    { id: 'search', icon: 'search', label: 'Search' },
  ];

  return (
    <div className="text-text-main flex h-screen overflow-hidden bg-soft-linen font-body-md antialiased">
      {/* SideNavBar (Desktop) */}
      <nav className="bg-surface-muted w-sidebar-width h-screen fixed left-0 top-0 hidden md:flex flex-col py-md z-40 border-r border-surface-variant/20">
        <div className="px-5 mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-container flex items-center justify-center text-primary font-headline-sm font-bold">SM</div>
            <div>
              <h2 className="font-headline-sm text-headline-sm text-primary">SlackMind</h2>
              <p className="font-label-md text-label-md text-text-subtle">Workspace KB</p>
            </div>
          </div>
        </div>

        <div className="flex-1 flex flex-col gap-2 mt-4">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`flex items-center gap-3 pl-5 py-3 transition-all duration-200 ${
                currentPage === item.id 
                  ? 'text-primary font-bold border-l-4 border-primary bg-surface/50 scale-[0.98]'
                  : 'text-on-surface-variant hover:bg-surface-container'
              }`}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span className="font-label-md text-label-md">{item.label}</span>
            </button>
          ))}
        </div>

        <div className="px-5 mb-6">
          <button 
            onClick={() => setCurrentPage('upload')}
            className="w-full bg-cherry-blossom text-on-primary py-3 rounded-lg font-label-md text-label-md hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined">upload</span>
            Upload Knowledge
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col md:ml-[280px] h-screen overflow-hidden relative">
        {currentPage === 'insights' && <InsightsDashboard />}
        {currentPage === 'admin' && <AdminDashboard />}
        {currentPage === 'upload' && <DocumentIngestion />}
        {currentPage === 'search' && <KnowledgeSearch />}
      </main>
    </div>
  );
}
