import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Audit Logs - Category Home
 * 
 * Platform: Observability & Evidence
 * Path: /observability/audit-logs
 */
export default function AuditLogsHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Audit Logs</h1>
          <nav className="breadcrumb">
            <span>Observability & Evidence</span>
            <span className="breadcrumb-separator">/</span>
            <span>Audit Logs</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Audit Logs. This workspace provides comprehensive tools and features
          for managing audit logs operations.
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
          
          <Link to="/observability/evidence" className="feature-link-card">
            <h3>Evidence Packs</h3>
            
          </Link>
          <Link to="/observability/evidence/query" className="feature-link-card">
            <h3>Evidence Queries</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/observability/evidence/export" className="feature-link-card">
            <h3>Export for Auditors</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/observability/retention" className="feature-link-card">
            <h3>Retention Policies</h3>
            
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