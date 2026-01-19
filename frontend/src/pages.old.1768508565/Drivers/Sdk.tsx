import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Driver SDK - Category Home
 * 
 * Platform: Drivers & Integrations
 * Path: /drivers/sdk
 */
export default function DriverSDKHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Driver SDK</h1>
          <nav className="breadcrumb">
            <span>Drivers & Integrations</span>
            <span className="breadcrumb-separator">/</span>
            <span>Driver SDK</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Driver SDK. This workspace provides comprehensive tools and features
          for managing driver sdk operations.
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
          
          <Link to="/integrations" className="feature-link-card">
            <h3>Overview</h3>
            
          </Link>
          <Link to="/drivers/registry" className="feature-link-card">
            <h3>Driver Registry</h3>
            
          </Link>
          <Link to="/drivers/testing" className="feature-link-card">
            <h3>Driver Testing & Validation</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/permissions" className="feature-link-card">
            <h3>Runtime Permissions</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/versioning" className="feature-link-card">
            <h3>Versioning & Deprecation</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/analytics" className="feature-link-card">
            <h3>Driver Analytics</h3>
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
