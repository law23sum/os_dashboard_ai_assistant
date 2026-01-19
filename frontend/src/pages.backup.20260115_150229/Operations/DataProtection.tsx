import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Data Loss Protection - Category Home
 * 
 * Platform: Operations & Infrastructure
 * Path: /operations/data-protection
 */
export default function DataLossProtectionHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Data Loss Protection</h1>
          <nav className="breadcrumb">
            <span>Operations & Infrastructure</span>
            <span className="breadcrumb-separator">/</span>
            <span>Data Loss Protection</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Data Loss Protection. This workspace provides comprehensive tools and features
          for managing data loss protection operations.
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
          
          <Link to="/operations/failure" className="feature-link-card">
            <h3>Failure Modes</h3>
            
          </Link>
          <Link to="/operations/detection" className="feature-link-card">
            <h3>Detection Mechanisms</h3>
            
          </Link>
          <Link to="/operations/recovery" className="feature-link-card">
            <h3>Recovery Strategies</h3>
            
          </Link>
          <Link to="/operations/bc-dr" className="feature-link-card">
            <h3>Business Continuity & DR</h3>
            
          </Link>
          <Link to="/operations/bc-dr/drills" className="feature-link-card">
            <h3>DR Drills</h3>
            <span className="badge badge-new">NEW</span>
          </Link>
          <Link to="/operations/security-incidents" className="feature-link-card">
            <h3>Security Incidents</h3>
            
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