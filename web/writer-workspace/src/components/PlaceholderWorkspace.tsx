import React from 'react';

interface PlaceholderWorkspaceProps {
  title: string;
  description: string;
}

export const PlaceholderWorkspace: React.FC<PlaceholderWorkspaceProps> = ({ title, description }) => {
  return (
    <div className="workspace">
      <div className="workspace-header">
        <div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
      </div>
      <div className="pane-card">
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
          <h3>Coming Soon</h3>
          <p>This workspace is currently under development.</p>
          <div style={{ marginTop: '20px', fontSize: '3rem' }}>🚧</div>
        </div>
      </div>
    </div>
  );
};
