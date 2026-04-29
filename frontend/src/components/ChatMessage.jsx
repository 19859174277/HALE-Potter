import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { User, Bot, AlertCircle } from 'lucide-react';

export default function ChatMessage({ msg, isError }) {
  const isUser = msg.role === 'user';

  // Replace placeholders with actual image URLs before rendering
  let processedContent = msg.content || '';
  if (msg.radarUrl) {
    processedContent = processedContent.replace(/RADAR_PLACEHOLDER/g, msg.radarUrl);
  }
  if (msg.sankeyUrl) {
    processedContent = processedContent.replace(/SANKEY_PLACEHOLDER/g, msg.sankeyUrl);
  }

  // Conservative markdown pre-processing
  function preprocessMarkdown(text) {
    if (!text) return text;

    // Step 1: Ensure blank line after display math blocks ($$...$$) to protect following content
    text = text.replace(/(\$\$[\s\S]*?\$\$)\n(?!\n)/g, '$1\n\n');

    // Step 2: Fix merged table lines and text-table mixing
    const lines = text.split('\n');
    const out = [];

    for (const raw of lines) {
      const line = raw.trimEnd();

      // Use a state machine to detect independent table blocks on the same line
      const blocks = [];
      let current = '';
      let inTable = false;

      for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (ch === '|') {
          if (!inTable) {
            // Starting a new table block
            if (current.trim()) {
              blocks.push({ type: 'text', content: current });
            }
            inTable = true;
            current = '|';
          } else {
            current += '|';
          }
        } else if (inTable) {
          current += ch;
        } else {
          current += ch;
        }
      }

      if (inTable && current) {
        blocks.push({ type: 'table', content: current });
      } else if (current) {
        blocks.push({ type: 'text', content: current });
      }

      // If multiple blocks detected, split them into separate lines
      if (blocks.length > 1) {
        for (const block of blocks) {
          out.push(block.content.trimEnd());
        }
      } else {
        out.push(line);
      }
    }

    text = out.join('\n');

    // Step 3: Remove blank lines INSIDE table blocks (header<->separator or row<->row)
    text = text.replace(/^(\|[^\n]*\|)\n\n(\s*\|)/gm, '$1\n$2');

    return text;
  }
  processedContent = preprocessMarkdown(processedContent);

  return (
    <div className={`flex gap-4 px-4 py-5 ${isUser ? 'bg-slate-50' : 'bg-transparent'}`}>
      <div className="shrink-0 mt-0.5">
        {isUser ? (
          <img
            src="/User.PNG"
            alt="User"
            className="w-8 h-8 rounded-full object-cover border border-slate-300"
            onError={(e) => {
              e.target.onerror = null;
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : (
          <img
            src="/HALE_Potter.PNG"
            alt="HALE-Potter"
            className="w-8 h-8 rounded-full object-cover border border-slate-300"
            onError={(e) => {
              e.target.onerror = null;
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        )}
        <div className="w-8 h-8 rounded-full bg-slate-100 items-center justify-center hidden">
          {isUser ? <User className="w-4 h-4 text-slate-500" /> : <Bot className="w-4 h-4 text-accent-blue" />}
        </div>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold text-slate-700">
            {isUser ? '用户' : 'HALE-Potter'}
          </span>
          {msg.timestamp && (
            <span className="text-[10px] text-slate-400">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>

        {isError ? (
          <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{msg.content}</span>
          </div>
        ) : (
          <div className="prose-dark max-w-none text-sm">
            {isUser ? (
              <p className="text-slate-800 whitespace-pre-wrap">{msg.content}</p>
            ) : (
              <ReactMarkdown
                remarkPlugins={[remarkMath, remarkGfm]}
                rehypePlugins={[rehypeKatex]}
                components={{
                  p: ({ node, ...props }) => <p className="mb-2" {...props} />,
                  table: ({ node, ...props }) => (
                    <div className="overflow-x-auto my-4 rounded-lg border border-slate-200">
                      <table {...props} />
                    </div>
                  ),
                  thead: ({ node, ...props }) => <thead {...props} />,
                  th: ({ node, ...props }) => <th {...props} />,
                  td: ({ node, ...props }) => <td {...props} />,
                  tr: ({ node, ...props }) => <tr {...props} />,
                  img: ({ node, ...props }) => (
                    <div className="my-4 rounded-lg overflow-hidden border border-slate-200 bg-white">
                      <img {...props} className="w-full h-auto object-contain max-h-[360px] max-w-[90%] mx-auto" loading="lazy" />
                    </div>
                  ),
                }}
              >
                {processedContent || ' '}
              </ReactMarkdown>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
