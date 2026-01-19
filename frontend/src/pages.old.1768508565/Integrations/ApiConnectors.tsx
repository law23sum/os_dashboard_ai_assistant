import React from 'react';
import { Link } from 'react-router-dom';

/**
 * API Connectors - Category Home
 * 
 * Platform: Drivers & Integrations
 * Path: /integrations/api-connectors
 */
export default function APIConnectorsHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">API Connectors</h1>
          <nav className="breadcrumb">
            <span>Drivers & Integrations</span>
            <span className="breadcrumb-separator">/</span>
            <span>API Connectors</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to API Connectors. This workspace provides comprehensive tools and features
          for managing api connectors operations.
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
          
          <Link to="/integrations/connectors" className="feature-link-card">
            <h3>Connectors Overview</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/integrations/credentials" className="feature-link-card">
            <h3>Credential Vault</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/integrations/productivity" className="feature-link-card">
            <h3>Productivity Suites</h3>
            
          </Link>
          <Link to="/drivers/integrations/code" className="feature-link-card">
            <h3>Code Hosts & CI/CD</h3>
            
          </Link>
          <Link to="/drivers/integrations/cloud" className="feature-link-card">
            <h3>Cloud Providers</h3>
            
          </Link>
          <Link to="/integrations/office" className="feature-link-card">
            <h3>Office Realtime</h3>
            
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
