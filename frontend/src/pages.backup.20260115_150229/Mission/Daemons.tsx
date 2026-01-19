import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Daemon Families - Category Home
 * 
 * Platform: Mission & Architecture
 * Path: /mission/daemons
 */
export default function DaemonFamiliesHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Daemon Families</h1>
          <nav className="breadcrumb">
            <span>Mission & Architecture</span>
            <span className="breadcrumb-separator">/</span>
            <span>Daemon Families</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Daemon Families. This workspace provides comprehensive tools and features
          for managing daemon families operations.
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
          
          <Link to="/mission/overview" className="feature-link-card">
            <h3>Mission & Scope</h3>
            
          </Link>
          <Link to="/mission/use-cases" className="feature-link-card">
            <h3>Use Cases Map</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/mission/non-goals" className="feature-link-card">
            <h3>System Boundaries & Non-Goals</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/mission/glossary" className="feature-link-card">
            <h3>Terminology Glossary</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/mission/modes" className="feature-link-card">
            <h3>Deployment Modes</h3>
            
          </Link>
          <Link to="/mission/reference-architectures" className="feature-link-card">
            <h3>Reference Architectures by Edition</h3>
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