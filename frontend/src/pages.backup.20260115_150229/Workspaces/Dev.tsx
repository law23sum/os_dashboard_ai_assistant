import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Dev Workspace - Category Home
 * 
 * Platform: Workspaces
 * Path: /workspaces/dev
 */
export default function DevWorkspaceHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Dev Workspace</h1>
          <nav className="breadcrumb">
            <span>Workspaces</span>
            <span className="breadcrumb-separator">/</span>
            <span>Dev Workspace</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Dev Workspace. This workspace provides comprehensive tools and features
          for managing dev workspace operations.
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
          
          <Link to="/work/tools" className="feature-link-card">
            <h3>Developer Tools</h3>
            
          </Link>
          <Link to="/workspaces/dev/repos" className="feature-link-card">
            <h3>Repo & Branch Browser</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/dev/cicd" className="feature-link-card">
            <h3>CI/CD Integration</h3>
            
          </Link>
          <Link to="/workspaces/dev/build-insights" className="feature-link-card">
            <h3>Build/Test Insights</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/workspaces/dev/commit-tasks" className="feature-link-card">
            <h3>Commit → Task Generator</h3>
            
          </Link>
          <Link to="/workspaces/dev/reviews" className="feature-link-card">
            <h3>Code Review Queue</h3>
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