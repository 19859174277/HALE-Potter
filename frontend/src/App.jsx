import { useState } from 'react';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import DataViewPage from './pages/DataViewPage';
import ConfigPage from './pages/ConfigPage';
import { useChat } from './hooks/useChat';
import { useConfig } from './hooks/useConfig';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const chat = useChat();
  const cfg = useConfig();

  const handleNewChat = () => {
    chat.createNewSession();
    setActiveTab('dashboard');
  };

  const handleSelectSession = (sessionId) => {
    chat.loadMessages(sessionId);
    setActiveTab('dashboard');
  };

  const handleDeleteSession = (sessionId) => {
    chat.deleteSession(sessionId);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-white text-slate-800">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        sessions={chat.sessions}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
      />
      <main className="flex-1 overflow-hidden">
        {activeTab === 'dashboard' && <DashboardPage chatState={chat} config={cfg.config} />}
        {activeTab === 'data' && <DataViewPage />}
        {activeTab === 'config' && <ConfigPage configState={cfg} />}
      </main>
    </div>
  );
}

export default App;
