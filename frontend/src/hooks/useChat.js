import { useState, useCallback, useRef, useEffect } from 'react';

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export function useChat() {
  const [sessions, setSessions] = useState([]);
  const [messages, setMessages] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const esRef = useRef(null);

  const loadSessions = useCallback(async () => {
    try {
      const res = await fetch('/api/chat/sessions');
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch (e) {
      console.error('Failed to load sessions', e);
    }
  }, []);

  const loadMessages = useCallback(async (sessionId) => {
    try {
      const res = await fetch(`/api/chat/history/${sessionId}`);
      const data = await res.json();
      // Parse images JSON and restore radar/sankey URLs for historical sessions
      const processedMessages = (data.messages || []).map((m) => {
        let images = [];
        try {
          images = typeof m.images === 'string' ? JSON.parse(m.images || '[]') : (m.images || []);
        } catch (e) {
          images = [];
        }
        return {
          ...m,
          images,
          radarUrl: images.find((url) => url.includes('radar')) || '',
          sankeyUrl: images.find((url) => url.includes('sankey')) || '',
        };
      });
      setMessages(processedMessages);
      setCurrentSessionId(sessionId);
      setError(null);
    } catch (e) {
      console.error('Failed to load messages', e);
    }
  }, []);

  const createNewSession = useCallback(() => {
    const id = generateUUID();
    setCurrentSessionId(id);
    setMessages([]);
    setError(null);
    setStatus(null);
    return id;
  }, []);

  const deleteSession = useCallback(async (sessionId) => {
    try {
      await fetch(`/api/chat/sessions/${sessionId}`, { method: 'DELETE' });
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
      if (currentSessionId === sessionId) {
        setMessages([]);
        setCurrentSessionId(null);
      }
    } catch (e) {
      console.error('Failed to delete session', e);
    }
  }, [currentSessionId]);

  const sendMessage = useCallback(async (text, alpha = 0.5517, beta = 0.0125) => {
    if (!text.trim()) return;
    const sessionId = currentSessionId || createNewSession();

    // Add user message locally
    const userMsg = { role: 'user', content: text, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);
    setStatus({ step: 'INIT', text: '正在建立智库连接...' });

    // Close any existing connection
    if (esRef.current) {
      esRef.current.close();
    }

    const es = new EventSource('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text, alpha, beta }),
    });

    // Note: EventSource doesn't support POST with body in all browsers.
    // As a fallback, we'll use fetch + ReadableStream parser for POST SSE.
    es.close();

    // Use fetch-based SSE parser for POST support
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text, alpha, beta }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let assistantContent = '';
    let currentImages = [];
    let radarUrl = '';
    let sankeyUrl = '';

    const processChunk = (chunk) => {
      buffer += decoder.decode(chunk, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line in buffer

      let eventName = '';
      let dataStr = '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventName = line.slice(6).trim();
        } else if (line.startsWith('data:')) {
          dataStr = line.slice(5).trim();
        } else if (line === '' && eventName) {
          try {
            const data = JSON.parse(dataStr || '{}');
            handleEvent(eventName, data);
          } catch (e) {
            // ignore parse errors
          }
          eventName = '';
          dataStr = '';
        }
      }
    };

    const handleEvent = (event, data) => {
      switch (event) {
        case 'status':
          setStatus({ step: data.step, text: data.text });
          break;
        case 'image':
          currentImages.push(data.url);
          if (data.type === 'radar') radarUrl = data.url;
          if (data.type === 'sankey') sankeyUrl = data.url;
          setMessages(prev => {
            const last = prev[prev.length - 1];
            if (last && last.role === 'assistant') {
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...last,
                images: [...(last.images || []), data.url],
                radarUrl: data.type === 'radar' ? data.url : (last.radarUrl || ''),
                sankeyUrl: data.type === 'sankey' ? data.url : (last.sankeyUrl || ''),
              };
              return updated;
            }
            return prev;
          });
          break;
        case 'delta':
          assistantContent += data.content;
          setMessages(prev => {
            const last = prev[prev.length - 1];
            if (last && last.role === 'assistant') {
              const updated = [...prev];
              updated[updated.length - 1] = { ...last, content: assistantContent };
              return updated;
            }
            return [...prev, { role: 'assistant', content: assistantContent, images: currentImages, radarUrl, sankeyUrl }];
          });
          break;
        case 'error':
          setError(data.message);
          setIsLoading(false);
          setStatus(null);
          break;
        case 'done':
          setIsLoading(false);
          setStatus(null);
          loadSessions();
          break;
        default:
          break;
      }
    };

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        processChunk(value);
      }
      // Process remaining buffer
      if (buffer.includes('event:')) {
        const lines = buffer.split('\n');
        let eventName = '';
        let dataStr = '';
        for (const line of lines) {
          if (line.startsWith('event:')) eventName = line.slice(6).trim();
          else if (line.startsWith('data:')) dataStr = line.slice(5).trim();
          else if (line === '' && eventName) {
            try { handleEvent(eventName, JSON.parse(dataStr || '{}')); } catch (e) {}
            eventName = '';
            dataStr = '';
          }
        }
      }
    } catch (e) {
      setError('连接中断，请重试');
    } finally {
      setIsLoading(false);
      setStatus(null);
      loadSessions();
    }
  }, [currentSessionId, createNewSession, loadSessions]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    sessions,
    messages,
    currentSessionId,
    status,
    isLoading,
    error,
    sendMessage,
    loadMessages,
    loadSessions,
    createNewSession,
    deleteSession,
  };
}
