import { useState, useEffect } from 'react';

export default function InsightsDashboard() {
  const [stats, setStats] = useState({ totalDocs: 0, processing: 0, failed: 0 });

  useEffect(() => {
    fetch('/api/documents')
      .then(res => res.json())
      .then(data => {
        setStats(prev => ({ ...prev, totalDocs: Array.isArray(data) ? data.length : (data.documents?.length || 0) }));
      })
      .catch(console.error);
  }, []);

  return (
    <div className="overflow-y-auto h-full">
      <header className="bg-surface sticky top-0 z-30 border-b border-surface-variant/20 flex justify-between items-center h-16 px-gutter max-w-container-max mx-auto w-full">
        <div className="flex gap-6 items-center">
          <h2 className="font-headline-md text-headline-md font-bold text-primary md:hidden">SlackMind</h2>
          <span className="hidden md:block font-headline-md text-headline-md font-bold text-primary mr-4">Insights</span>
        </div>
        <div className="flex gap-4 items-center">
          <button className="text-on-surface-variant hover:bg-surface-container-low p-2 rounded-full"><span className="material-symbols-outlined">notifications</span></button>
          <div className="w-8 h-8 rounded-full border border-outline-variant bg-primary-container flex items-center justify-center text-primary font-bold">U</div>
        </div>
      </header>

      <div className="p-gutter max-w-container-max mx-auto w-full pb-xl">
        <div className="mb-lg mt-sm">
          <h2 className="font-headline-lg text-headline-lg text-text-main mb-2">Knowledge Insights</h2>
          <p className="font-body-md text-body-md text-text-subtle">A comprehensive overview of your workspace intelligence.</p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-lg">
          <div className="bg-surface rounded-lg p-6 border border-subtle hover-lift ambient-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="bg-surface-muted p-2 rounded-lg">
                <span className="material-symbols-outlined text-primary">description</span>
              </div>
            </div>
            <p className="font-label-md text-label-md text-text-subtle mb-1">Total Documents Indexed</p>
            <h3 className="font-headline-lg text-headline-lg text-text-main">{stats.totalDocs}</h3>
          </div>

          <div className="bg-surface rounded-lg p-6 border border-subtle hover-lift ambient-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="bg-cherry-blossom/20 p-2 rounded-lg">
                <span className="material-symbols-outlined text-primary">search_check</span>
              </div>
            </div>
            <p className="font-label-md text-label-md text-text-subtle mb-1">Successful Queries</p>
            <h3 className="font-headline-lg text-headline-lg text-text-main">89.2%</h3>
          </div>

          <div className="bg-surface rounded-lg p-6 border border-subtle hover-lift ambient-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="bg-surface-muted p-2 rounded-lg">
                <span className="material-symbols-outlined text-primary">group</span>
              </div>
            </div>
            <p className="font-label-md text-label-md text-text-subtle mb-1">Team Participation</p>
            <h3 className="font-headline-lg text-headline-lg text-text-main">142</h3>
          </div>
        </div>

        {/* Charts & Search Terms */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-surface rounded-lg border border-subtle p-6 lg:col-span-2 ambient-shadow">
            <div className="flex justify-between items-center mb-6">
              <h4 className="font-headline-sm text-headline-sm text-text-main">Knowledge Base Growth</h4>
            </div>
            <div className="h-64 relative flex items-end w-full gap-2 px-2 border-l border-b border-surface-variant">
              <div className="w-1/6 bg-surface-muted h-1/4 rounded-t-sm"></div>
              <div className="w-1/6 bg-surface-muted h-1/3 rounded-t-sm"></div>
              <div className="w-1/6 bg-surface-muted h-1/2 rounded-t-sm"></div>
              <div className="w-1/6 bg-cherry-blossom/60 h-2/3 rounded-t-sm"></div>
              <div className="w-1/6 bg-cherry-blossom/80 h-3/4 rounded-t-sm"></div>
              <div className="w-1/6 bg-primary h-full rounded-t-sm"></div>
            </div>
          </div>

          <div className="bg-surface rounded-lg border border-subtle p-6 ambient-shadow flex flex-col">
            <h4 className="font-headline-sm text-headline-sm text-text-main mb-6">Most Searched Terms</h4>
            <ul className="flex flex-col gap-4 flex-1">
              <li className="flex items-center justify-between">
                <span className="font-body-md text-body-md text-text-main">HR Policies</span>
                <div className="w-16 h-2 bg-surface-muted rounded-full overflow-hidden"><div className="h-full bg-primary w-[90%]"></div></div>
              </li>
              <li className="flex items-center justify-between">
                <span className="font-body-md text-body-md text-text-main">Onboarding Process</span>
                <div className="w-16 h-2 bg-surface-muted rounded-full overflow-hidden"><div className="h-full bg-cherry-blossom w-[75%]"></div></div>
              </li>
              <li className="flex items-center justify-between">
                <span className="font-body-md text-body-md text-text-main">Architecture Spec</span>
                <div className="w-16 h-2 bg-surface-muted rounded-full overflow-hidden"><div className="h-full bg-primary-fixed-dim w-[60%]"></div></div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
