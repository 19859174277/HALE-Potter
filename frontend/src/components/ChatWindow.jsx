import { useState, useRef, useEffect } from 'react';
import { Send, AlertTriangle } from 'lucide-react';
import ChatMessage from './ChatMessage';
import StatusIndicator from './StatusIndicator';

export default function ChatWindow({
  messages,
  status,
  isLoading,
  error,
  onSend,
  alpha,
  beta,
}) {
  const [input, setInput] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, status]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 px-6">
            <h2 className="text-2xl font-light text-slate-700 mb-2">HALE-Potter 智库助手</h2>
            <p className="text-sm text-center max-w-md leading-relaxed">
              输入国家名称（如“中国”或“印度”），我将自动生成多维健康系统诊断雷达图、
              Pareto 资源重组桑基图，并调用 Kimi 政策模型撰写高规格决策建议。
            </p>
            <div className="mt-6 flex gap-2">
              {['生成中国的健康寻优方案', '看看日本的卫生体系', '分析印度的资源配置'].map((demo) => (
                <button
                  key={demo}
                  onClick={() => onSend(demo)}
                  className="px-3 py-1.5 rounded-full text-xs bg-white border border-slate-200 text-slate-500 hover:text-slate-800 hover:border-slate-400 transition-colors"
                >
                  {demo}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <ChatMessage key={idx} msg={msg} />
        ))}

        {error && (
          <ChatMessage
            msg={{ role: 'assistant', content: error, timestamp: new Date().toISOString() }}
            isError
          />
        )}

        <StatusIndicator status={status} isLoading={isLoading} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 bg-slate-50/80 backdrop-blur-sm p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="输入国家名称或智库问题..."
            rows={1}
            className="w-full bg-white border border-slate-300 rounded-xl pl-4 pr-12 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/30 resize-none"
            style={{ minHeight: '48px', maxHeight: '200px' }}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-accent-blue text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-accent-blue/90 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-center text-[10px] text-slate-400 mt-2 flex items-center justify-center gap-1">
          <AlertTriangle className="w-3 h-3" />
          HALE-Potter 可能生成不准确的卫生政策建议，仅供研究参考。
        </p>
      </div>
    </div>
  );
}
