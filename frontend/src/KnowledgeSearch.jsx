import { useState, useRef, useEffect } from 'react';

export default function KnowledgeSearch() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Good afternoon. What knowledge can I retrieve for you today?',
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    const conversation_history = messages.filter(m => m.role === 'user' || m.role === 'assistant');

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage, conversation_history }),
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer || "I'm sorry, an error occurred.",
        sources: data.sources || []
      }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I failed to fetch an answer.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e) => {
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  return (
    <div className="flex flex-col h-full relative bg-surface-muted/30">
      <header className="bg-surface sticky top-0 z-30 border-b border-surface-variant/20 flex justify-between items-center h-16 px-gutter max-w-container-max mx-auto w-full">
        <div className="flex gap-6 items-center">
          <h2 className="font-headline-md text-headline-md font-bold text-primary md:hidden">SlackMind</h2>
          <span className="hidden md:block font-headline-md text-headline-md font-bold text-primary mr-4">Search</span>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-gutter relative max-w-container-max mx-auto w-full pb-32">
        <div className="max-w-3xl mx-auto space-y-8 mt-lg">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-fade-in flex items-start gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-cherry-blossom text-on-primary flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="material-symbols-outlined text-[18px]">smart_toy</span>
                </div>
              )}
              
              <div className={`text-text-main font-body-md text-body-md p-5 rounded-xl max-w-[85%] border shadow-sm ${
                msg.role === 'user' 
                  ? 'bg-surface-container rounded-tr-none border-surface-variant/50' 
                  : 'bg-surface rounded-tl-none border-outline-variant/30'
              }`}>
                <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-5 bg-surface-container-low rounded-lg p-4 border border-outline-variant/20">
                    <h4 className="font-label-md text-label-md text-text-subtle mb-3 uppercase tracking-wider flex items-center gap-2">
                      <span className="material-symbols-outlined text-[16px]">menu_book</span>
                      Sources Used
                    </h4>
                    <ul className="space-y-2">
                      {msg.sources.map((src, i) => (
                        <li key={i}>
                          <div className="group flex items-center gap-3 p-2 rounded-md hover:bg-surface-container transition-colors border border-transparent hover:border-outline-variant/10">
                            <div className="w-8 h-8 rounded bg-tertiary-container/30 flex items-center justify-center text-tertiary shrink-0">
                              <span className="material-symbols-outlined text-[16px]">
                                {src.source?.startsWith('http') ? 'link' : 'description'}
                              </span>
                            </div>
                            <div className="flex-1 overflow-hidden">
                              <p className="font-body-sm text-body-sm text-primary font-medium truncate">{src.source || 'Unknown source'}</p>
                              {src.tags && <p className="font-label-md text-[10px] text-text-subtle truncate opacity-80 mt-0.5">{src.tags}</p>}
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full border border-outline-variant bg-primary-container flex items-center justify-center text-primary font-bold flex-shrink-0 mt-1">U</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-start gap-4 chat-fade-in">
              <div className="w-8 h-8 rounded-full bg-cherry-blossom text-on-primary flex items-center justify-center flex-shrink-0 mt-1">
                <span className="material-symbols-outlined text-[18px]">smart_toy</span>
              </div>
              <div className="bg-surface p-5 rounded-xl rounded-tl-none border border-outline-variant/30 shadow-sm flex gap-1 items-center h-12">
                <div className="w-2 h-2 rounded-full bg-cherry-blossom animate-bounce" style={{animationDelay: '0ms'}}></div>
                <div className="w-2 h-2 rounded-full bg-cherry-blossom animate-bounce" style={{animationDelay: '150ms'}}></div>
                <div className="w-2 h-2 rounded-full bg-cherry-blossom animate-bounce" style={{animationDelay: '300ms'}}></div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area (Fixed Bottom) */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-soft-linen via-soft-linen/90 to-transparent pt-10 pb-6 px-gutter z-20 pointer-events-none">
        <div className="max-w-3xl mx-auto relative pointer-events-auto">
          <div className="bg-surface rounded-xl border border-outline-variant/50 shadow-lg focus-within:border-cherry-blossom focus-within:ring-2 focus-within:ring-cherry-blossom/20 transition-all duration-300 flex items-end p-2 gap-2">
            <textarea 
              ref={textareaRef}
              value={input}
              onChange={(e) => { setInput(e.target.value); handleInput(e); }}
              onKeyDown={handleKeyDown}
              className="w-full bg-transparent border-none focus:ring-0 resize-none max-h-32 py-3 px-2 font-body-md text-body-md text-text-main placeholder:text-text-subtle/50 outline-none" 
              placeholder="Ask a question about your workspace..." 
              rows="1"
            />
            <button 
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="p-3 bg-cherry-blossom text-on-primary rounded-lg hover:bg-primary transition-colors flex-shrink-0 shadow-sm self-end mb-0.5 disabled:opacity-50"
            >
              <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>send</span>
            </button>
          </div>
          <div className="text-center mt-3">
            <p className="font-label-md text-[11px] text-text-subtle">SlackMind AI can make mistakes. Verify important information.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
