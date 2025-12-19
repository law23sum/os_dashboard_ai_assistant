# Environment Setup Guide

## Overview

OS Dashboard supports multiple deployment environments:
- **local/dev**: Development environment (unit testing) - treated as interchangeable
- **alpha/beta**: Integrated testing environments
- **prod/release**: Production environment (real user data testing)

## Environment Configuration

### Local/Dev Environment

**Purpose**: Local development and unit testing

**Setup**:
```bash
# Copy example config
cp .env.local.example .env.local

# Start backend
cd backend_api
python -m uvicorn main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend
npm install
npm run dev
```

**Database**: Uses local SQLite database at `assistant_hub_gui/assistant_hub/assistant_hub.db`

**API Base**: `http://localhost:8000/api`
**Frontend URL**: `http://localhost:5173`

### Alpha/Beta Environment

**Purpose**: Integrated testing with shared infrastructure

**Setup**:
```bash
# Copy example config
cp .env.alpha.example .env.alpha

# Set environment variables
export VITE_API_BASE=https://alpha-api.osdashboard.ai/api
export VITE_FRONTEND_URL=https://alpha.osdashboard.ai
export ENVIRONMENT=alpha
```

**Features**:
- Shared test database
- CI/CD integration
- Automated test execution

### Prod/Release Environment

**Purpose**: Production deployment with real user data

**Setup**:
```bash
# Copy example config
cp .env.prod.example .env.prod

# Set environment variables
export VITE_API_BASE=https://api.osdashboard.ai/api
export VITE_FRONTEND_URL=https://osdashboard.ai
export ENVIRONMENT=prod
```

**Features**:
- Production database
- SSL/TLS encryption
- Monitoring and alerting
- Backup and recovery

## Running Tests

### E2E Test Suite

```bash
# Run all tests in local environment
./tests/e2e/test-runner.sh local all

# Run specific test type
./tests/e2e/test-runner.sh local sanity
./tests/e2e/test-runner.sh local functional
./tests/e2e/test-runner.sh local regression

# Run in different environments
./tests/e2e/test-runner.sh alpha all
./tests/e2e/test-runner.sh beta all
./tests/e2e/test-runner.sh prod all
```

### Test Types

1. **Sanity Tests**: Quick smoke tests to verify basic functionality
2. **Functional Tests**: Comprehensive CRUD and feature tests
3. **Regression Tests**: Tests to prevent breaking changes

## Deployment

### Local/Dev Deployment

```bash
# Build frontend
cd frontend
npm run build

# Start backend with built frontend
cd backend_api
python -m uvicorn main:app --port 8000
```

### Production Deployment

```bash
# Build for production
cd frontend
npm run build -- --mode production

# Deploy backend
# (Use your deployment method: Docker, Kubernetes, etc.)
```

## Environment Variables

### Required Variables

- `VITE_API_BASE`: Backend API base URL
- `VITE_FRONTEND_URL`: Frontend URL
- `ENVIRONMENT`: Environment name (local, dev, alpha, beta, prod, release)

### Optional Variables

- `DATABASE_PATH`: Database file path (defaults to standard location)
- `NODE_ENV`: Node environment (development, production)
- `TEST_ENV`: Test environment override

## Database Management

### Local Database

The local database is SQLite located at:
`assistant_hub_gui/assistant_hub/assistant_hub.db`

### Backup and Restore

```bash
# Backup database
cp assistant_hub_gui/assistant_hub/assistant_hub.db assistant_hub_gui/assistant_hub/assistant_hub.db.backup

# Restore database
cp assistant_hub_gui/assistant_hub/assistant_hub.db.backup assistant_hub_gui/assistant_hub/assistant_hub.db
```

## Troubleshooting

### Backend Not Starting

1. Check if port 8000 is available
2. Verify Python dependencies: `pip install -r backend_api/requirements.txt`
3. Check database permissions

### Frontend Not Connecting

1. Verify `VITE_API_BASE` is set correctly
2. Check CORS settings in backend
3. Verify backend is running

### Tests Failing

1. Ensure backend is running
2. Check environment variables
3. Verify database is accessible
4. Check test logs for specific errors
