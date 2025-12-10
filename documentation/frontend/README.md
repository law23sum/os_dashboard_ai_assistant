# OS Dashboard AI Assistant - Frontend

Modern React/TypeScript frontend that works on both web browsers and desktop (Electron).

## Quick Start

```bash
# Install dependencies
npm install

# Start development
npm run dev
# Choose: 1 for Web Browser, 2 for Desktop App
```

## Features

- ✅ **Unified Codebase** - Single React codebase for web and desktop
- ✅ **Cross-Platform** - Linux, Windows, macOS support
- ✅ **Modern Stack** - React 18, TypeScript, Vite, Tailwind CSS
- ✅ **Hot Reload** - Fast development with instant updates
- ✅ **Type Safety** - Full TypeScript coverage
- ✅ **Responsive** - Works on desktop and mobile browsers

## Project Structure

```
frontend/
├── src/
│   ├── pages/          # Page components
│   ├── components/     # Shared components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # API clients
│   ├── utils/          # Utilities
│   └── types/          # TypeScript types
├── electron/           # Electron main process
├── scripts/           # Build scripts
└── dist/              # Production builds
```

## Available Scripts

- `npm run dev` - Start development (asks for mode)
- `npm run dev:web` - Web browser only
- `npm run dev:desktop` - Desktop app only
- `npm run build:web` - Build for web
- `npm run build:desktop` - Build desktop app
- `npm run build:all` - Build for all platforms

## Documentation

- [Migration Guide](../MIGRATION_GUIDE.md) - Migration from Tkinter
- [Migration Status](./MIGRATION_STATUS.md) - Current migration status
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and fixes
- [Quick Start](./QUICK_START.md) - Quick reference

## Requirements

- Node.js 16+
- Backend server on port 8000 (for full functionality)

## License

See main project LICENSE file.

