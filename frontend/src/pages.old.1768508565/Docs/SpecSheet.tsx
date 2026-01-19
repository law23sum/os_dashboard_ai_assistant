import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Technical Spec Sheet - Category Home
 * 
 * Platform: Docs & Spec
 * Path: /docs/spec-sheet
 */
export default function TechnicalSpecSheetHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Technical Spec Sheet</h1>
          <nav className="breadcrumb">
            <span>Docs & Spec</span>
            <span className="breadcrumb-separator">/</span>
            <span>Technical Spec Sheet</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Technical Spec Sheet. This workspace provides comprehensive tools and features
          for managing technical spec sheet operations.
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
          
          <Link to="/docs" className="feature-link-card">
            <h3>Docs Hub</h3>
            
          </Link>
          <Link to="/docs/getting-started" className="feature-link-card">
            <h3>Getting Started</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/docs/tutorials" className="feature-link-card">
            <h3>Tutorials</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/docs/glossary" className="feature-link-card">
            <h3>Glossary</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/docs/release-notes" className="feature-link-card">
            <h3>Release Notes</h3>
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
