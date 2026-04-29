import { useState, useEffect } from 'react';
import { Save, Key, SlidersHorizontal, Globe } from 'lucide-react';

export default function ConfigForm({ config, loading, saved, onSave }) {
  const [form, setForm] = useState({
    kimi_api_key: '',
    kimi_base_url: 'https://api.kimi.com/coding/',
    alpha: 0.5517,
    beta: 0.0125,
  });

  useEffect(() => {
    if (config) {
      setForm((prev) => ({
        ...prev,
        ...config,
        kimi_api_key: config.kimi_api_key || '',
      }));
    }
  }, [config]);

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);
  };

  return (
    <div className="h-full flex flex-col bg-white p-6 max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-slate-800 mb-1">系统配置</h2>
        <p className="text-sm text-slate-500">管理 Kimi API 连接与 HALE-Potter 模型参数</p>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm">加载配置中...</div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-5 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <Globe className="w-4 h-4 text-accent-blue" />
              <h3 className="text-sm font-semibold text-slate-800">Kimi API 设置</h3>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1.5">API Base URL</label>
              <input
                type="text"
                value={form.kimi_base_url}
                onChange={(e) => handleChange('kimi_base_url', e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:border-accent-blue"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1.5">API Key</label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="password"
                  value={form.kimi_api_key}
                  onChange={(e) => handleChange('kimi_api_key', e.target.value)}
                  placeholder="sk-kimi-..."
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-10 pr-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-accent-blue"
                />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                当前使用的是 Kimi Code Anthropic 兼容端点。模型固定为 kimi-k2.5。
              </p>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-5 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <SlidersHorizontal className="w-4 h-4 text-accent-cyan" />
              <h3 className="text-sm font-semibold text-slate-800">MO-QPO 寻优参数</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1.5">
                  α 效率权重 (Alpha)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  max="1"
                  value={form.alpha}
                  onChange={(e) => handleChange('alpha', parseFloat(e.target.value))}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:border-accent-blue"
                />
                <p className="text-[10px] text-slate-400 mt-1">资金配置对因果弹性 (CATE) 的敏感系数</p>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1.5">
                  β 摩擦系数 (Beta / Friction)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  max="1"
                  value={form.beta}
                  onChange={(e) => handleChange('beta', parseFloat(e.target.value))}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:border-accent-blue"
                />
                <p className="text-[10px] text-slate-400 mt-1">部门间资源重组的二次摩擦惩罚</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-accent-blue text-white text-sm font-medium hover:bg-accent-blue/90 transition-colors"
            >
              <Save className="w-4 h-4" />
              保存配置
            </button>
            {saved && (
              <span className="text-xs text-emerald-600">配置已保存</span>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
