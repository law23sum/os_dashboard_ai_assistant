import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Vertical Editions - Category Home
 * 
 * Platform: Drivers & Integrations
 * Path: /drivers/vertical-editions
 */
export default function VerticalEditionsHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Vertical Editions</h1>
          <nav className="breadcrumb">
            <span>Drivers & Integrations</span>
            <span className="breadcrumb-separator">/</span>
            <span>Vertical Editions</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Vertical Editions. This workspace provides comprehensive tools and features
          for managing vertical editions operations.
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
          
          <Link to="/drivers/marketplace" className="feature-link-card">
            <h3>Marketplace</h3>
            
          </Link>
          <Link to="/drivers/marketplace/reviews" className="feature-link-card">
            <h3>Reviews & Ratings</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/marketplace/security-review" className="feature-link-card">
            <h3>Security Review Pipeline</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/packs" className="feature-link-card">
            <h3>Driver Packs</h3>
            
          </Link>
          <Link to="/drivers/packs/builder" className="feature-link-card">
            <h3>Pack Builder</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/drivers/enterprise-store" className="feature-link-card">
            <h3>Enterprise App Store</h3>
            
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
