import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Third-Party Risk - Category Home
 * 
 * Platform: Drivers & Integrations
 * Path: /drivers/risk
 */
export default function DriversRiskPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Third-Party Risk</h1>
          <nav className="breadcrumb">
            <span>Drivers & Integrations</span>
            <span className="breadcrumb-separator">/</span>
            <span>Third-Party Risk</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Third-Party Risk. This workspace provides comprehensive tools and features
          for managing third-party risk operations.
        </p>
      </div>


      {/* Environment */}
      <EnvironmentSection />

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
          
          <Link to="/drivers/risk/overview" className="feature-link-card">
            <h3>Risk & Governance Overview</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/risk/vendors" className="feature-link-card">
            <h3>Vendor Inventory</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/risk/assessments" className="feature-link-card">
            <h3>Risk Assessments</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/risk/remediation" className="feature-link-card">
            <h3>Remediation Tracker</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/risk/exceptions" className="feature-link-card">
            <h3>Exceptions & Approvals</h3>
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