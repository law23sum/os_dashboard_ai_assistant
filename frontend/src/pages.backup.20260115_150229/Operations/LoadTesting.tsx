import React from 'react';
import { Link } from 'react-router-dom';
import EnvironmentSection from '@/components/EnvironmentSection';

/**
 * Load Testing - Category Home
 * 
 * Platform: Operations & Infrastructure
 * Path: /operations/load-testing
 */
export default function LoadTestingHome() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Load Testing</h1>
          <nav className="breadcrumb">
            <span>Operations & Infrastructure</span>
            <span className="breadcrumb-separator">/</span>
            <span>Load Testing</span>
          </nav>
        </div>
      </div>

      {/* Overview */}
      <div className="section">
        <h2>Overview</h2>
        <p className="text-muted">
          Welcome to Load Testing. This workspace provides comprehensive tools and features
          for managing load testing operations.
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
          
          <Link to="/operations/performance" className="feature-link-card">
            <h3>Performance</h3>
            
          </Link>
          <Link to="/operations/scaling" className="feature-link-card">
            <h3>Scaling Strategies</h3>
            
          </Link>
          <Link to="/operations/capacity" className="feature-link-card">
            <h3>Capacity Planning</h3>
            
          </Link>
          <Link to="/operations/backpressure" className="feature-link-card">
            <h3>Backpressure & Throttling</h3>
            
          </Link>
          <Link to="/operations/reliability" className="feature-link-card">
            <h3>Reliability Patterns</h3>
            
          </Link>
          <Link to="/operations/driver-performance" className="feature-link-card">
            <h3>Driver Performance</h3>
            
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