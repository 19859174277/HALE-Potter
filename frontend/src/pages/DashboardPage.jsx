import ChatWindow from '../components/ChatWindow';

export default function DashboardPage({ chatState, config }) {
  return (
    <div className="h-full">
      <ChatWindow
        messages={chatState.messages}
        status={chatState.status}
        isLoading={chatState.isLoading}
        error={chatState.error}
        onSend={chatState.sendMessage}
        alpha={config?.alpha ?? 0.5517}
        beta={config?.beta ?? 0.0125}
      />
    </div>
  );
}
