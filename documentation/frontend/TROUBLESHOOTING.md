# Troubleshooting Guide

## Web Page and Desktop App Not Displaying

### Issue: Blank Screen or "No workspace data available"

#### 1. Check Backend Server
The frontend requires the backend API to be running:

```bash
# Start the backend server
uvicorn ai_os.app.main:app --reload
```

The backend should be accessible at `http://localhost:8000`

#### 2. Check Frontend Dev Server
```bash
cd frontend
npm install  # If you haven't already
npm run dev
```

Choose option 1 for web browser or 2 for desktop app.

#### 3. Verify API Connection
Open browser DevTools (F12) and check:
- Network tab: Are API requests failing?
- Console tab: Any JavaScript errors?

#### 4. Check Vite Proxy Configuration
The `vite.config.ts` should proxy `/api` requests to `http://localhost:8000`

If backend is on a different port, update:
```typescript
proxy: {
  "/api": {
    target: "http://localhost:YOUR_PORT",
    changeOrigin: true,
  }
}
```

### Issue: Tailwind CSS Not Working

If styles aren't applying:

1. **Verify Tailwind is installed:**
   ```bash
   npm list tailwindcss
   ```

2. **Check `tailwind.config.js` exists** in `frontend/` directory

3. **Verify `postcss.config.js` exists** in `frontend/` directory

4. **Check `index.css` has Tailwind directives:**
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

5. **Restart dev server** after adding Tailwind config

### Issue: Components Not Rendering

1. **Check browser console** for React errors
2. **Verify all imports** are correct
3. **Check that `#root` element exists** in `index.html`

### Issue: Desktop App (Electron) Not Launching

1. **Ensure web server is running first:**
   ```bash
   npm run dev:web-only
   ```

2. **Then in another terminal:**
   ```bash
   npm run electron:dev
   ```

3. **Or use the combined command:**
   ```bash
   npm run dev:desktop
   ```

### Issue: API Requests Failing

1. **Check CORS settings** on backend
2. **Verify API endpoints** exist and are responding
3. **Check network tab** for actual request URLs
4. **Verify proxy configuration** in `vite.config.ts`

### Quick Fixes

**Clear cache and reinstall:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Check for TypeScript errors:**
```bash
npm run build
```

**Verify all dependencies:**
```bash
npm install
```

### Common Error Messages

**"Failed to fetch"**
- Backend server not running
- Wrong API URL
- CORS issue

**"Module not found"**
- Missing dependency: `npm install`
- Wrong import path

**"Cannot read property of undefined"**
- API response structure mismatch
- Missing error handling

### Still Not Working?

1. Check `frontend/package.json` has all required dependencies
2. Verify Node.js version (should be 16+)
3. Check that ports 5173 (Vite) and 8000 (backend) are available
4. Review browser console and terminal output for errors

