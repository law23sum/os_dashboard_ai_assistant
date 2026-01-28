import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Multi-Region & DR - Category Home
 * 
 * Platform: Operations & Infrastructure
 * Path: /operations/multi-region
 */
export default function OperationsMultiRegionPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Multi-Region & DR</h1>
          <nav className="breadcrumb">
            <span>Operations & Infrastructure</span>
            <span className="breadcrumb-separator">/</span>
            <span>Multi-Region & DR</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Multi-Region & DR. This workspace provides comprehensive tools and features
          for managing multi-region & dr operations.
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
          
          <Link to="/operations/config" className="feature-link-card">
            <h3>Configuration Management</h3>
            
          </Link>
          <Link to="/operations/secrets" className="feature-link-card">
            <h3>Secrets & Configuration Vault</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/operations/cluster" className="feature-link-card">
            <h3>Compute/Cluster Management</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/operations/topology" className="feature-link-card">
            <h3>Network Topology</h3>
            
          </Link>
          <Link to="/systems/network" className="feature-link-card">
            <h3>Network Monitoring</h3>
            
          </Link>
          <Link to="/operations/storage" className="feature-link-card">
            <h3>Storage Topology</h3>
            
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
