import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Digital Twin Builder - Category Home
 * 
 * Platform: Workspaces
 * Path: /workspaces/twins
 */
export default function DigitalTwinBuilderHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Digital Twin Builder</h1>
          <nav className="breadcrumb">
            <span>Workspaces</span>
            <span className="breadcrumb-separator">/</span>
            <span>Digital Twin Builder</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Digital Twin Builder. This workspace provides comprehensive tools and features
          for managing digital twin builder operations.
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
          
          <Link to="/workspaces/twins/templates" className="feature-link-card">
            <h3>Twin Templates</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/twins/feeds" className="feature-link-card">
            <h3>Data Feeds & Sync</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/twins/scenarios" className="feature-link-card">
            <h3>Scenario Runner</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/twins/reality-mesh" className="feature-link-card">
            <h3>Reality Twin Mesh</h3>
            
          </Link>
          <Link to="/workspaces/twins/governance" className="feature-link-card">
            <h3>Twin Governance</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/twins/enterprise" className="feature-link-card">
            <h3>Enterprise Twin</h3>
            
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
