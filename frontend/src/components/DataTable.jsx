import { useState, useEffect } from 'react';
import { Search, ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';

export default function DataTable() {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('HALE_Percentile');
  const [order, setOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const limit = 20;

  const columns = [
    { key: 'ISO_Code', label: 'ISO' },
    { key: 'Country_Name', label: '国家/地区' },
    { key: 'HALE_Percentile', label: 'HALE 百分位' },
    { key: 'DEA_Efficiency_Percentile', label: 'DEA 效率百分位' },
    { key: 'Fund_Input_Percentile', label: '投入百分位' },
    { key: 'Physician_Coverage_Percentile', label: '医师覆盖百分位' },
    { key: 'PM25_Burden_Control_Percentile', label: 'PM2.5 控制百分位' },
    { key: 'Tobacco_Burden_Control_Percentile', label: '烟草控制百分位' },
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `/api/data/countries?sort_by=${sortBy}&order=${order}&limit=${limit}&page=${page}&search=${encodeURIComponent(search)}`
      );
      const json = await res.json();
      setData(json.countries || []);
      setTotal(json.total || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [sortBy, order, search, page]);

  const toggleSort = (key) => {
    if (sortBy === key) {
      setOrder(order === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(key);
      setOrder('desc');
    }
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-1">数据透视</h2>
        <p className="text-sm text-slate-500">全球 190 国健康系统底座指标一览</p>
      </div>

      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索国家或 ISO 代码..."
            className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-accent-blue"
          />
        </div>
      </div>

      <div className="flex-1 overflow-auto border border-slate-200 rounded-xl">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 sticky top-0 z-10">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => toggleSort(col.key)}
                  className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-slate-800 select-none border-b border-slate-200"
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    <ArrowUpDown className="w-3 h-3 opacity-50" />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">
                  加载中...
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">
                  无匹配数据
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  {columns.map((col) => (
                    <td key={col.key} className="px-4 py-2.5 text-slate-700 whitespace-nowrap">
                      {typeof row[col.key] === 'number'
                        ? row[col.key].toFixed(2)
                        : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-4 text-xs text-slate-500">
        <span>共 {total} 条记录</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page <= 1}
            className="p-1 rounded hover:bg-slate-100 disabled:opacity-30"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span>第 {page} 页</span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={data.length < limit}
            className="p-1 rounded hover:bg-slate-100 disabled:opacity-30"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
