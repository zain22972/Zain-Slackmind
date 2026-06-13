import { useState, useEffect } from 'react';

export default function AdminDashboard() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/documents')
      .then(res => res.json())
      .then(data => {
        setDocuments(Array.isArray(data) ? data : (data.documents || []));
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="overflow-y-auto h-full">
      <header className="bg-surface sticky top-0 z-30 border-b border-surface-variant/20 flex justify-between items-center h-16 px-gutter max-w-container-max mx-auto w-full">
        <div className="flex gap-6 items-center">
          <h2 className="font-headline-md text-headline-md font-bold text-primary md:hidden">SlackMind</h2>
          <span className="hidden md:block font-headline-md text-headline-md font-bold text-primary mr-4">Documents</span>
        </div>
        <div className="flex gap-4 items-center">
          <button className="text-on-surface-variant hover:bg-surface-container-low p-2 rounded-full"><span className="material-symbols-outlined">notifications</span></button>
          <div className="w-8 h-8 rounded-full border border-outline-variant bg-primary-container flex items-center justify-center text-primary font-bold">U</div>
        </div>
      </header>

      <div className="p-gutter lg:p-lg xl:px-xl max-w-container-max mx-auto w-full">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-lg gap-4">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-text-main">Knowledge Repository</h2>
            <p className="font-body-md text-body-md text-text-subtle mt-2">Manage and monitor ingested Slack data and documentation.</p>
          </div>
          <div className="relative w-full md:w-64">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-subtle">search</span>
            <input 
              type="text" 
              className="w-full pl-10 pr-4 py-2 bg-surface rounded-lg border border-outline-variant/30 focus:border-cherry-blossom focus:ring-2 focus:ring-cherry-blossom/20 transition-all font-body-sm text-body-sm outline-none" 
              placeholder="Search documents..." 
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-md mb-xl">
          <div className="bg-surface rounded-xl p-md border border-outline-variant/10 ambient-shadow hover-lift">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">database</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm text-text-subtle">Total Indexed</h3>
            </div>
            <div className="font-headline-lg text-headline-lg text-text-main">{documents.length}</div>
          </div>
          
          <div className="bg-surface rounded-xl p-md border border-outline-variant/10 ambient-shadow hover-lift">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-secondary-container/30 flex items-center justify-center text-secondary">
                <span className="material-symbols-outlined">memory</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm text-text-subtle">Processing</h3>
            </div>
            <div className="font-headline-lg text-headline-lg text-text-main">0</div>
          </div>

          <div className="bg-surface rounded-xl p-md border border-outline-variant/10 ambient-shadow hover-lift">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-error-container/30 flex items-center justify-center text-error">
                <span className="material-symbols-outlined">error_outline</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm text-text-subtle">Failed</h3>
            </div>
            <div className="font-headline-lg text-headline-lg text-text-main">0</div>
          </div>
        </div>

        <div className="bg-surface rounded-xl border border-outline-variant/10 overflow-hidden shadow-sm mb-xl">
          <div className="border-b border-outline-variant/20 px-md py-4 flex justify-between items-center bg-surface-muted/30">
            <h3 className="font-headline-sm text-headline-sm">Recent Documents</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant/20 bg-surface-muted/10 font-label-md text-label-md text-text-subtle">
                  <th className="p-md font-semibold">Name</th>
                  <th className="p-md font-semibold">Tags</th>
                  <th className="p-md font-semibold">Scope</th>
                  <th className="p-md font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="font-body-sm text-body-sm">
                {loading && <tr><td colSpan="4" className="p-md text-center">Loading...</td></tr>}
                {!loading && documents.length === 0 && <tr><td colSpan="4" className="p-md text-center">No documents found.</td></tr>}
                {documents.map((doc, idx) => (
                  <tr key={idx} className="border-b border-outline-variant/10 hover:bg-surface-muted/20 transition-colors group cursor-pointer">
                    <td className="p-md font-medium text-text-main flex items-center gap-3">
                      <span className="material-symbols-outlined text-text-subtle">
                        {doc.source?.startsWith('http') ? 'link' : 'description'}
                      </span>
                      {doc.source || 'Unknown'}
                    </td>
                    <td className="p-md text-text-subtle">
                      {Array.isArray(doc.tags) ? doc.tags.join(', ') : (doc.tags || 'untagged')}
                    </td>
                    <td className="p-md">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-surface-muted text-on-surface-variant">
                        {doc.scope || 'org'}
                      </span>
                    </td>
                    <td className="p-md">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-tertiary-container/30 text-on-tertiary-container">
                        <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span> Indexed
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
