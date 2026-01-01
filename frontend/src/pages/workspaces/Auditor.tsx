import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Record Auditor - Category Home
 * 
 * Platform: Workspaces (Enterprise Extensions)
 * Path: /workspaces/auditor
 */
export default function RecordAuditorHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Record Auditor</h1>
          <nav className="breadcrumb">
            <span>Workspaces (Enterprise Extensions)</span>
            <span className="breadcrumb-separator">/</span>
            <span>Record Auditor</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Record Auditor. This workspace provides comprehensive tools and features
          for managing record auditor operations.
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
          
          <Link to="/workspaces/auditor/evidence" className="feature-link-card">
            <h3>Evidence Trails</h3>
            
          </Link>
          <Link to="/workspaces/auditor/controls" className="feature-link-card">
            <h3>Controls Mapping</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/auditor/requests" className="feature-link-card">
            <h3>Evidence Requests</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/auditor/reports" className="feature-link-card">
            <h3>Audit Reports</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/auditor/logbook" className="feature-link-card">
            <h3>Immutable Logbook Viewer</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/auditor/regulator" className="feature-link-card">
            <h3>Regulator Views</h3>
            
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
