import React from 'react';
import { Link } from 'react-router-dom';

/**
 * API Keys - Category Home
 * 
 * Platform: Settings & Admin
 * Path: /settings/api-keys
 */
export default function APIKeysHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">API Keys</h1>
          <nav className="breadcrumb">
            <span>Settings & Admin</span>
            <span className="breadcrumb-separator">/</span>
            <span>API Keys</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to API Keys. This workspace provides comprehensive tools and features
          for managing api keys operations.
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
          
          <Link to="/settings" className="feature-link-card">
            <h3>Settings</h3>
            
          </Link>
          <Link to="/settings/profile" className="feature-link-card">
            <h3>User Profile</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/settings/preferences" className="feature-link-card">
            <h3>Preferences</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/settings/notifications" className="feature-link-card">
            <h3>Notifications</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/settings/credentials" className="feature-link-card">
            <h3>Integrations Credentials</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/settings/account" className="feature-link-card">
            <h3>Account Settings</h3>
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
