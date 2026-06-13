import { useState, useRef } from 'react';

export default function DocumentIngestion() {
  const [scope, setScope] = useState('org');
  const [tags, setTags] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState('');
  const fileInputRef = useRef(null);

  const handleUpload = async (file) => {
    if (!file) return;
    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('scope', scope);
    formData.append('tags', tags);

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) setStatus('success');
      else setStatus('error');
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  };

  const handleUrlSubmit = async () => {
    if (!urlInput) return;
    setStatus('uploading');
    try {
      const res = await fetch('/api/documents/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlInput, scope, tags }),
      });
      if (res.ok) {
        setStatus('success');
        setUrlInput('');
      } else setStatus('error');
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  };

  return (
    <div className="overflow-y-auto h-full">
      <header className="bg-surface sticky top-0 z-30 border-b border-surface-variant/20 flex justify-between items-center h-16 px-gutter max-w-container-max mx-auto w-full">
        <div className="flex gap-6 items-center">
          <h2 className="font-headline-md text-headline-md font-bold text-primary md:hidden">SlackMind</h2>
          <span className="hidden md:block font-headline-md text-headline-md font-bold text-primary mr-4">Ingest Knowledge</span>
        </div>
      </header>

      <div className="p-gutter lg:p-lg flex justify-center items-start min-h-[calc(100vh-64px)] w-full">
        <div className="w-full max-w-[800px] flex flex-col gap-lg pb-xl">
          <div className="text-center mb-md mt-sm">
            <h1 className="font-headline-lg text-headline-lg text-text-main mb-xs">Ingest Knowledge</h1>
            <p className="font-body-lg text-body-lg text-text-subtle">Upload documents or URLs to expand the workspace intelligence.</p>
          </div>

          {status === 'success' && (
            <div className="bg-tertiary-container/30 text-on-tertiary-container p-4 rounded-lg text-center font-bold">
              Successfully ingested!
            </div>
          )}
          {status === 'error' && (
            <div className="bg-error-container/30 text-error p-4 rounded-lg text-center font-bold">
              Failed to ingest. Please try again.
            </div>
          )}

          {/* Upload Zone */}
          <div 
            className={`w-full border-2 border-dashed rounded-xl bg-surface p-xl text-center cursor-pointer transition-all duration-300 flex flex-col items-center justify-center relative overflow-hidden ${isDragging ? 'drag-active border-cherry-blossom' : 'border-outline-variant/60 hover:border-cherry-blossom/50 hover:bg-surface-container-low'}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleUpload(e.dataTransfer.files[0]); }}
            onClick={() => fileInputRef.current?.click()}
          >
            <input type="file" ref={fileInputRef} className="hidden" onChange={(e) => handleUpload(e.target.files[0])} />
            <div className="flex gap-4 mb-6 relative z-10">
              <div className="w-14 h-14 rounded-lg bg-surface-muted flex items-center justify-center text-primary soft-shadow-hover"><span className="material-symbols-outlined text-3xl">picture_as_pdf</span></div>
              <div className="w-14 h-14 rounded-lg bg-surface-muted flex items-center justify-center text-primary soft-shadow-hover"><span className="material-symbols-outlined text-3xl">article</span></div>
            </div>
            <h3 className="font-headline-sm text-headline-sm text-text-main mb-2">Drag & Drop files here</h3>
            <p className="font-body-sm text-body-sm text-text-subtle mb-6">or click to browse from your computer</p>
            <button className="px-6 py-2 border border-outline-variant rounded-lg font-label-md text-label-md text-text-main hover:bg-surface-muted transition-colors">
              Browse Files
            </button>
          </div>

          <div className="text-center font-body-sm text-text-subtle">- OR -</div>

          {/* URL Input */}
          <div className="flex gap-2 w-full">
            <input 
              type="text" 
              value={urlInput}
              onChange={e => setUrlInput(e.target.value)}
              placeholder="https://example.com/document" 
              className="flex-1 bg-surface border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md focus:outline-none focus:border-cherry-blossom focus:ring-2 focus:ring-cherry-blossom/20 transition-all text-text-main placeholder:text-text-subtle/50"
            />
            <button 
              onClick={handleUrlSubmit}
              disabled={status === 'uploading'}
              className="px-6 py-3 bg-cherry-blossom text-on-primary rounded-lg font-label-md hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              Ingest URL
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-lg w-full">
            {/* Metadata Selection */}
            <div className="bg-surface rounded-xl p-md border border-outline-variant/30 flex flex-col gap-6 soft-shadow-hover">
              <h3 className="font-headline-sm text-headline-sm text-text-main border-b border-outline-variant/20 pb-3">Classification</h3>
              <div className="flex flex-col gap-4">
                <label className="font-label-md text-label-md text-text-subtle">Visibility Scope</label>
                <div className="flex flex-wrap gap-3">
                  {['org', 'team', 'private'].map(s => (
                    <label key={s} className="cursor-pointer">
                      <input 
                        type="radio" 
                        name="scope" 
                        checked={scope === s} 
                        onChange={() => setScope(s)} 
                        className="peer sr-only" 
                      />
                      <div className="px-4 py-2 rounded-full border border-outline-variant text-text-subtle peer-checked:bg-primary-container peer-checked:text-on-primary-container peer-checked:border-primary transition-colors font-label-md text-label-md flex items-center gap-2 capitalize">
                        <span className="material-symbols-outlined text-[18px]">
                          {s === 'org' ? 'corporate_fare' : s === 'team' ? 'groups' : 'lock'}
                        </span>
                        {s} Scope
                      </div>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <label className="font-label-md text-label-md text-text-subtle">Custom Tags</label>
                <input 
                  type="text" 
                  value={tags}
                  onChange={e => setTags(e.target.value)}
                  className="w-full bg-transparent border border-outline-variant rounded-lg px-4 py-2 font-body-md text-body-md focus:outline-none focus:border-cherry-blossom focus:ring-2 focus:ring-cherry-blossom/20 transition-all text-text-main placeholder:text-text-subtle/50" 
                  placeholder="e.g. HR, Onboarding..." 
                />
              </div>
            </div>

            {/* Progress Pipeline */}
            <div className="bg-surface rounded-xl p-md border border-outline-variant/30 flex flex-col gap-6 soft-shadow-hover">
              <h3 className="font-headline-sm text-headline-sm text-text-main border-b border-outline-variant/20 pb-3">Ingestion Pipeline</h3>
              <div className="flex flex-col gap-0 relative pl-4 mt-2">
                <div className="absolute left-[23px] top-4 bottom-4 w-0.5 bg-outline-variant/30"></div>
                
                <div className={`flex items-start gap-4 relative py-3 ${status === 'uploading' ? '' : 'opacity-50'}`}>
                  <div className="w-6 h-6 rounded-full border-2 border-cherry-blossom bg-surface flex items-center justify-center z-10 shrink-0 mt-0.5 relative">
                    {status === 'uploading' && <div className="w-2 h-2 rounded-full bg-cherry-blossom animate-pulse"></div>}
                  </div>
                  <div>
                    <h4 className={`font-label-md text-label-md ${status === 'uploading' ? 'text-primary font-bold' : 'text-text-main'}`}>
                      {status === 'uploading' ? 'Processing...' : 'Awaiting Input'}
                    </h4>
                  </div>
                </div>

                <div className={`flex items-start gap-4 relative py-3 ${status === 'success' ? '' : 'opacity-50'}`}>
                  <div className="w-6 h-6 rounded-full border-2 border-outline-variant bg-surface z-10 shrink-0 mt-0.5">
                    {status === 'success' && <span className="material-symbols-outlined text-[14px] text-tertiary">check</span>}
                  </div>
                  <div>
                    <h4 className="font-label-md text-label-md text-text-main">Knowledge Indexing</h4>
                    <p className="font-body-sm text-body-sm text-text-subtle mt-1">Ready for semantic search.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
