import ConfigForm from '../components/ConfigForm';

export default function ConfigPage({ configState }) {
  return (
    <div className="h-full overflow-y-auto">
      <ConfigForm
        config={configState.config}
        loading={configState.loading}
        saved={configState.saved}
        onSave={configState.saveConfig}
      />
    </div>
  );
}
