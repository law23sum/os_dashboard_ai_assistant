import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Logging & Tracing Overview - Category Home
 * 
 * Platform: Observability & Evidence
 * Path: /observability/logging-tracing
 */
export default function LoggingTracingOverviewHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Logging & Tracing Overview</h1>
          <nav className="breadcrumb">
            <span>Observability & Evidence</span>
            <span className="breadcrumb-separator">/</span>
            <span>Logging & Tracing Overview</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Logging & Tracing Overview. This workspace provides comprehensive tools and features
          for managing logging & tracing overview operations.
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
          
          <Link to="/observability/logging" className="feature-link-card">
            <h3>Structured Logging</h3>
            
          </Link>
          <Link to="/observability/logging/explorer" className="feature-link-card">
            <h3>Log Explorer</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/observability/tracing" className="feature-link-card">
            <h3>Distributed Tracing</h3>
            
          </Link>
          <Link to="/observability/tracing/explorer" className="feature-link-card">
            <h3>Trace Explorer</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/observability/correlation" className="feature-link-card">
            <h3>Correlation & Context</h3>
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