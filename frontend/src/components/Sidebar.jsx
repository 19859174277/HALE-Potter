import { useState } from 'react';
import {
  MessageSquare,
  BarChart3,
  Settings,
  Plus,
  ChevronLeft,
  ChevronRight,
  Trash2,
} from 'lucide-react';

export default function Sidebar({ activeTab, onTabChange, sessions, onSelectSession, onNewChat, onDeleteSession }) {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { id: 'dashboard', label: '智库看板', icon: MessageSquare },
    { id: 'data', label: '数据透视', icon: BarChart3 },
    { id: 'config', label: '系统配置', icon: Settings },
  ];

  return (
    <aside
      className={`flex flex-col bg-slate-50 border-r border-slate-200 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-72'
      }`}
    >
      <div className="flex items-center justify-between px-4 py-4 border-b border-slate-200">
        <div className="flex items-center gap-3 overflow-hidden">
          <img
            src="/HALE_Potter.PNG"
            alt="HALE-Potter"
            className="w-8 h-8 rounded-full object-cover border border-slate-700 shrink-0"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          {!collapsed && (
            <div className="whitespace-nowrap">
              <h1 className="text-sm font-bold text-slate-800 tracking-wide">HALE-Potter</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">Policy Intelligence</p>
            </div>
          )}
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded hover:bg-slate-200 text-slate-500"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      <div className="p-3">
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-lg bg-accent-blue/10 text-accent-blue hover:bg-accent-blue/20 transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4 shrink-0" />
          {!collapsed && <span>新建对话</span>}
        </button>
      </div>

      <nav className="px-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors ${
                active
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800'
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span className="whitespace-nowrap">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {!collapsed && (
        <div className="flex-1 overflow-y-auto px-3 py-4">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">
            历史会话
          </p>
          <div className="space-y-1">
            {sessions.map((s) => (
              <div
                key={s.session_id}
                className="group flex items-center gap-1 w-full px-2 py-1.5 rounded text-left text-xs text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <button
                  onClick={() => onSelectSession(s.session_id)}
                  className="flex items-center gap-2 flex-1 min-w-0 text-left"
                  title={s.title || 'New Chat'}
                >
                  <MessageSquare className="w-3 h-3 shrink-0 text-slate-500" />
                  <span className="truncate">{s.title || 'New Chat'}</span>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.session_id);
                  }}
                  className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-100 hover:text-red-600 transition-all shrink-0"
                  title="删除会话"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {collapsed && <div className="flex-1" />}

      <div className="p-4 border-t border-slate-200">
        {!collapsed && (
          <p className="text-[10px] text-slate-600">
            HALE-Potter v1.0<br />
            Global Health Resource Optimizer
          </p>
        )}
      </div>
    </aside>
  );
}
