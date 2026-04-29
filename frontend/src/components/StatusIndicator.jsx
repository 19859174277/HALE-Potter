import { Loader2, Search, Radar, GitBranch, FileText, FileDown, CheckCircle } from 'lucide-react';

const STEPS = [
  { key: 'INIT', label: '建立连接', icon: Loader2 },
  { key: 'NER', label: '检索数据库', icon: Search },
  { key: 'RADAR', label: '雷达诊断', icon: Radar },
  { key: 'SANKEY', label: 'MO-QPO 寻优', icon: GitBranch },
  { key: 'POLICY', label: '政策撰写', icon: FileText },
  { key: 'REPORT', label: '研报落盘', icon: FileDown },
];

export default function StatusIndicator({ status, isLoading }) {
  if (!isLoading || !status) return null;

  const currentIdx = STEPS.findIndex((s) => s.key === status.step);

  return (
    <div className="flex items-center gap-1 px-4 py-3 bg-white/90 border border-slate-200 rounded-xl backdrop-blur-sm shadow-sm mb-4">
      {STEPS.map((step, idx) => {
        const Icon = step.icon;
        const isActive = idx === currentIdx;
        const isDone = idx < currentIdx;

        return (
          <div key={step.key} className="flex items-center gap-1">
            <div
              className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium transition-all ${
                isActive
                  ? 'bg-accent-blue/15 text-accent-blue animate-pulse'
                  : isDone
                  ? 'text-emerald-400'
                  : 'text-slate-400'
              }`}
            >
              {isDone ? (
                <CheckCircle className="w-3.5 h-3.5" />
              ) : (
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'animate-spin' : ''}`} />
              )}
              <span className="hidden sm:inline">{step.label}</span>
            </div>
            {idx < STEPS.length - 1 && (
              <div
                className={`w-4 h-px ${isDone ? 'bg-emerald-500/40' : 'bg-slate-300'}`}
              />
            )}
          </div>
        );
      })}
      <span className="ml-2 text-xs text-slate-500 truncate max-w-[200px]">{status.text}</span>
    </div>
  );
}
