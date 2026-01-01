import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Archive Workspace - Category Home
 * 
 * Platform: Workspaces
 * Path: /workspaces/archive
 */
export default function ArchiveWorkspaceHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Archive Workspace</h1>
          <nav className="breadcrumb">
            <span>Workspaces</span>
            <span className="breadcrumb-separator">/</span>
            <span>Archive Workspace</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Archive Workspace. This workspace provides comprehensive tools and features
          for managing archive workspace operations.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="section">
        <h2>Quick Actions</h2>
        <div className="quick-actions-grid">
          <button className="quick-action-card">
            <span className="action-icon">+</span>
            <span className="action-label">Create New</span>
          </button>
          <button className="quick-action-card">
            <span className="action-icon">▶</span>
            <span className="action-label">Run</span>
          </button>
          <button className="quick-action-card">
            <span className="action-icon">↓</span>
            <span className="action-label">Import</span>
          </button>
        </div>
      </div>

      {/* Quick Links to Top Features */}
      <div className="section">
        <h2>Top Features</h2>
        <div className="feature-links-grid">
          
          <Link to="/workspaces/archive/snapshots" className="feature-link-card">
            <h3>Snapshot Manager</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/archive/retention" className="feature-link-card">
            <h3>Retention Policies</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/archive/time-travel" className="feature-link-card">
            <h3>Temporal Reconstruction</h3>
            
          </Link>
          <Link to="/workspaces/archive/restore" className="feature-link-card">
            <h3>Restore & Export</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          <p className="text-muted">No recent activity</p>
        </div>
      </div>

      {/* Getting Started */}
      <div className="section">
        <h2>Getting Started</h2>
        <div className="checklist">
          <div className="checklist-item">
            <input type="checkbox" id="step1" />
            <label htmlFor="step1">Complete initial setup</label>
          </div>
          <div className="checklist-item">
            <input type="checkbox" id="step2" />
            <label htmlFor="step2">Configure preferences</label>
          </div>
          <div className="checklist-item">
            <input type="checkbox" id="step3" />
            <label htmlFor="step3">Explore key features</label>
          </div>
        </div>
      </div>
    </div>
  );
}
