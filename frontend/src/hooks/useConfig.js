import { useState, useEffect, useCallback } from 'react';

export function useConfig() {
  const [config, setConfig] = useState({
    kimi_api_key: '',
    kimi_base_url: 'https://api.kimi.com/coding/',
    alpha: 0.5517,
    beta: 0.0125,
  });
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  const loadConfig = useCallback(async () => {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      setConfig(prev => ({ ...prev, ...data }));
    } catch (e) {
      console.error('Failed to load config', e);
    } finally {
      setLoading(false);
    }
  }, []);

  const saveConfig = useCallback(async (newConfig) => {
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig),
      });
      if (res.ok) {
        setConfig(newConfig);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      }
    } catch (e) {
      console.error('Failed to save config', e);
    }
  }, []);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  return { config, loading, saved, saveConfig };
}
