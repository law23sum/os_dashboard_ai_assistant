import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Major Components - Category Home
 * 
 * Platform: Mission & Architecture
 * Path: /mission/components
 */
export default function MajorComponentsHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Major Components</h1>
          <nav className="breadcrumb">
            <span>Mission & Architecture</span>
            <span className="breadcrumb-separator">/</span>
            <span>Major Components</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Major Components. This workspace provides comprehensive tools and features
          for managing major components operations.
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
          
          <Link to="/mission/architecture" className="feature-link-card">
            <h3>Architecture Overview</h3>
            
          </Link>
          <Link to="/mission/principles" className="feature-link-card">
            <h3>Architectural Principles</h3>
            
          </Link>
          <Link to="/mission/orchestrator" className="feature-link-card">
            <h3>Driver-Aware Orchestrator</h3>
            
          </Link>
          <Link to="/mission/mapping" className="feature-link-card">
            <h3>Component Mapping</h3>
            
          </Link>
          <Link to="/mission/contracts" className="feature-link-card">
            <h3>Data Model & Contracts</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/mission/extensibility" className="feature-link-card">
            <h3>Extensibility Points</h3>
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